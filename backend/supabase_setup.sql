-- ============================================
-- NOVACURE ULTRA-MINIMAL SCHEMA (7 TABLES)
-- This fully satisfies the data requirements but uses JSONB 
-- to dramatically speed up remaining development.
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. PROFILES (Auth Service)
-- Maps Supabase users to their role and branch string.
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'pharmacist' CHECK (role IN ('admin', 'pharmacist', 'warehouse_supervisor', 'regional_manager')),
    branch_code TEXT, -- e.g. 'HYD-01'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. PRODUCTS (Inventory Service)
-- The global pharmacy catalog.
-- ============================================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    category TEXT,
    reorder_threshold INTEGER DEFAULT 10,
    is_controlled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. INVENTORY (Inventory Service)
-- Consolidates strict batch tracking and quantities.
-- ============================================
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_code TEXT NOT NULL,
    batch_number TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, branch_code, batch_number)
);

-- ============================================
-- 4. SALES (Sales Service)
-- Consolidates Orders, Invoices, line items into JSONB.
-- ============================================
CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_code TEXT NOT NULL,
    pharmacist_id UUID REFERENCES profiles(id),
    customer_name TEXT,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    payment_status TEXT DEFAULT 'paid' CHECK (payment_status IN ('unpaid', 'paid', 'credit')),
    items JSONB NOT NULL, -- e.g. [{"product_id": "...", "qty": 2, "price": 10.0}]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 5. PURCHASE ORDERS (Purchase Service)
-- Consolidates Vendors, line items, and received Goods status.
-- ============================================
CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_name TEXT NOT NULL,
    branch_code TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'received', 'cancelled')),
    items JSONB NOT NULL, -- e.g. [{"product_id": "...", "qty_ordered": 100, "qty_received": 100}]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 6. TRANSFERS (Inventory Service)
-- Manages intra-branch stock movements directly.
-- ============================================
CREATE TABLE IF NOT EXISTS transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_branch_code TEXT NOT NULL,
    to_branch_code TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    items JSONB NOT NULL, -- e.g. [{"product_id": "...", "batch_number": "...", "qty": 10}]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 7. AI EVENTS (AI & Alerts Service)
-- Scalable unified sink for all background job flags.
-- ============================================
CREATE TABLE IF NOT EXISTS ai_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL CHECK (event_type IN ('forecast', 'anomaly', 'query', 'alert')),
    branch_code TEXT,
    reference_id UUID, 
    data JSONB NOT NULL, -- Flexible payload payload 
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'accepted', 'dismissed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users read own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Admins full access" ON profiles FOR ALL USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin'));

ALTER TABLE products ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Read products" ON products FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Manage products" ON products FOR ALL USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'warehouse_supervisor')));

ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Read inventory" ON inventory FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Manage inventory" ON inventory FOR ALL USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'warehouse_supervisor')));

ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Pharmacists create sales" ON sales FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'pharmacist')));
CREATE POLICY "Read own branch sales" ON sales FOR SELECT USING (
    branch_code = (SELECT branch_code FROM profiles WHERE id = auth.uid()) OR EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
);

ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Read POs" ON purchase_orders FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Manage POs" ON purchase_orders FOR ALL USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'warehouse_supervisor')));

ALTER TABLE transfers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Read transfers" ON transfers FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Manage transfers" ON transfers FOR ALL USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'warehouse_supervisor')));

ALTER TABLE ai_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Read ai events" ON ai_events FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Update ai events" ON ai_events FOR UPDATE USING (auth.role() = 'authenticated');
