-- ════════════════════════════════════════════════════════════════════
-- CARNET — Admin Backend Migration
-- Date : 12 mai 2026
-- Author : Sly + Claude
-- Description : Role admin + RLS + audit log + KPIs RPC
-- ════════════════════════════════════════════════════════════════════

-- ─── 1. Add role column to profiles ─────────────────────────────────
-- Note : assumes a 'profiles' table exists (created by Supabase auth trigger)

ALTER TABLE profiles 
  ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user' 
  CHECK (role IN ('user', 'admin', 'moderator'));

CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role) 
  WHERE role <> 'user';


-- ─── 2. is_admin() helper function ──────────────────────────────────

CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN
LANGUAGE SQL
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() AND role = 'admin'
  );
$$;

GRANT EXECUTE ON FUNCTION is_admin() TO authenticated;


-- ─── 3. admin_audit_log table ───────────────────────────────────────

CREATE TABLE IF NOT EXISTS admin_audit_log (
  id BIGSERIAL PRIMARY KEY,
  admin_user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  admin_email TEXT,
  action TEXT NOT NULL,           -- toggle_status, delete, edit, bulk_archive, login
  target_table TEXT,              -- cars, donations, sources, profiles, system
  target_id TEXT,                 -- ID of affected row (text since cars.id is text)
  details JSONB,                  -- before/after values, reason, bulk count, etc.
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_admin_user ON admin_audit_log(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON admin_audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_table_action ON admin_audit_log(target_table, action);

ALTER TABLE admin_audit_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS audit_admin_select ON admin_audit_log;
CREATE POLICY audit_admin_select ON admin_audit_log
  FOR SELECT TO authenticated
  USING (is_admin());

DROP POLICY IF EXISTS audit_admin_insert ON admin_audit_log;
CREATE POLICY audit_admin_insert ON admin_audit_log
  FOR INSERT TO authenticated
  WITH CHECK (is_admin());


-- ─── 4. RLS policies for admin write access on cars ─────────────────

-- Note : assumes cars table already has RLS enabled and a public-read policy

DROP POLICY IF EXISTS cars_admin_all ON cars;
CREATE POLICY cars_admin_all ON cars
  FOR ALL TO authenticated
  USING (is_admin())
  WITH CHECK (is_admin());

DROP POLICY IF EXISTS cars_archive_admin_all ON cars_archive;
CREATE POLICY cars_archive_admin_all ON cars_archive
  FOR ALL TO authenticated
  USING (is_admin())
  WITH CHECK (is_admin());


-- ─── 5. RLS for donations (admin read all, including pending) ───────

DROP POLICY IF EXISTS donations_admin_read ON donations;
CREATE POLICY donations_admin_read ON donations
  FOR SELECT TO authenticated
  USING (is_admin());


-- ─── 6. get_admin_kpis() — all dashboard stats in 1 call ────────────

CREATE OR REPLACE FUNCTION get_admin_kpis()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  result JSONB;
BEGIN
  IF NOT is_admin() THEN
    RAISE EXCEPTION 'Forbidden : admin role required';
  END IF;
  
  SELECT jsonb_build_object(
    'cars_active', (
      SELECT COUNT(*) FROM cars WHERE status = 'active'
    ),
    'cars_archived', (
      SELECT COUNT(*) FROM cars_archive
    ),
    'cars_added_today', (
      SELECT COUNT(*) FROM cars 
      WHERE created_at >= NOW() - INTERVAL '24 hours' AND status = 'active'
    ),
    'cars_added_week', (
      SELECT COUNT(*) FROM cars 
      WHERE created_at >= NOW() - INTERVAL '7 days' AND status = 'active'
    ),
    'avg_score', (
      SELECT ROUND(AVG(sc)::NUMERIC, 1) 
      FROM cars WHERE status = 'active' AND sc IS NOT NULL
    ),
    'premium_count', (
      SELECT COUNT(*) FROM cars 
      WHERE status = 'active' AND px >= 100000
    ),
    'premier_count', (
      SELECT COUNT(*) FROM cars 
      WHERE status = 'active' AND px >= 500000
    ),
    'hyper_count', (
      SELECT COUNT(*) FROM cars 
      WHERE status = 'active' AND px >= 1000000
    ),
    'sources_active', (
      SELECT COUNT(DISTINCT src) FROM cars 
      WHERE status = 'active' AND created_at >= NOW() - INTERVAL '7 days'
    ),
    'brands_active', (
      SELECT COUNT(DISTINCT mk) FROM cars WHERE status = 'active'
    ),
    'donations_total_eur', (
      SELECT COALESCE(SUM(amount_eur)::NUMERIC, 0) 
      FROM donations WHERE status = 'signed'
    ),
    'donations_count_signed', (
      SELECT COUNT(*) FROM donations WHERE status = 'signed'
    ),
    'donations_count_pending', (
      SELECT COUNT(*) FROM donations WHERE status = 'pending'
    ),
    'top_sources', (
      SELECT jsonb_agg(t) FROM (
        SELECT src, COUNT(*) AS cnt 
        FROM cars 
        WHERE status = 'active' 
        GROUP BY src 
        ORDER BY cnt DESC 
        LIMIT 10
      ) t
    ),
    'top_brands', (
      SELECT jsonb_agg(t) FROM (
        SELECT mk, COUNT(*) AS cnt 
        FROM cars 
        WHERE status = 'active' 
        GROUP BY mk 
        ORDER BY cnt DESC 
        LIMIT 10
      ) t
    ),
    'cars_by_day_14d', (
      SELECT jsonb_agg(t ORDER BY t->>'day') FROM (
        SELECT jsonb_build_object(
          'day', TO_CHAR(d.day::DATE, 'YYYY-MM-DD'),
          'cnt', COUNT(c.id)
        ) AS t
        FROM generate_series(
          NOW() - INTERVAL '13 days', 
          NOW(), 
          INTERVAL '1 day'
        ) d(day)
        LEFT JOIN cars c ON DATE(c.created_at) = d.day::DATE AND c.status = 'active'
        GROUP BY d.day
      ) days
    )
  ) INTO result;
  
  RETURN result;
END;
$$;

GRANT EXECUTE ON FUNCTION get_admin_kpis() TO authenticated;


-- ─── 7. get_source_stats() — per-source breakdown ───────────────────

CREATE OR REPLACE FUNCTION get_source_stats()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NOT is_admin() THEN
    RAISE EXCEPTION 'Forbidden : admin role required';
  END IF;
  
  RETURN (
    SELECT jsonb_agg(t ORDER BY t->>'total' DESC) FROM (
      SELECT jsonb_build_object(
        'source', src,
        'total', COUNT(*),
        'active', COUNT(*) FILTER (WHERE status = 'active'),
        'archived_via_wash', COUNT(*) FILTER (WHERE status = 'expired'),
        'avg_score', ROUND(AVG(sc)::NUMERIC, 1) FILTER (WHERE sc IS NOT NULL),
        'avg_price', ROUND(AVG(px)::NUMERIC, 0) FILTER (WHERE px IS NOT NULL AND px > 0),
        'last_seen', MAX(created_at)
      ) AS t
      FROM cars
      GROUP BY src
    ) sources
  );
END;
$$;

GRANT EXECUTE ON FUNCTION get_source_stats() TO authenticated;


-- ─── 8. log_admin_action() — wrapper for audit logging ──────────────

CREATE OR REPLACE FUNCTION log_admin_action(
  p_action TEXT,
  p_target_table TEXT DEFAULT NULL,
  p_target_id TEXT DEFAULT NULL,
  p_details JSONB DEFAULT NULL
) RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_email TEXT;
  v_id BIGINT;
BEGIN
  IF NOT is_admin() THEN
    RAISE EXCEPTION 'Forbidden : admin role required';
  END IF;
  
  SELECT email INTO v_email FROM auth.users WHERE id = auth.uid();
  
  INSERT INTO admin_audit_log (
    admin_user_id, admin_email, action, target_table, target_id, details
  ) VALUES (
    auth.uid(), v_email, p_action, p_target_table, p_target_id, p_details
  )
  RETURNING id INTO v_id;
  
  RETURN v_id;
END;
$$;

GRANT EXECUTE ON FUNCTION log_admin_action(TEXT, TEXT, TEXT, JSONB) TO authenticated;


-- ─── 9. Promote Sly to admin (RUN ONCE après ton premier login) ─────
-- ⚠️ Décommente ces lignes et remplace par ton vrai email après login

-- UPDATE profiles SET role = 'admin' WHERE email = 'sly@carnet.life';
-- UPDATE profiles SET role = 'admin' WHERE email = 'auth@carnet.life';


-- ─── 10. Verification queries ───────────────────────────────────────
-- Pour vérifier après migration :

-- SELECT id, email, role FROM profiles WHERE role = 'admin';
-- SELECT is_admin();  -- Devrait retourner true si tu es loggé en admin
-- SELECT get_admin_kpis();  -- Devrait retourner les stats
-- SELECT * FROM admin_audit_log ORDER BY created_at DESC LIMIT 10;
