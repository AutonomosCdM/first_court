-- Create canvas tables
-- Enable RLS and set up policies

-- Canvas Nodes Table
CREATE TABLE canvas_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    position JSONB NOT NULL DEFAULT '{"x": 0, "y": 0}',
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES auth.users(id),
    metadata JSONB,
    CONSTRAINT valid_position CHECK (
        position ? 'x' AND 
        position ? 'y' AND 
        jsonb_typeof(position->'x') = 'number' AND 
        jsonb_typeof(position->'y') = 'number'
    )
);

-- Canvas Edges Table
CREATE TABLE canvas_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES canvas_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES canvas_nodes(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES auth.users(id)
);

-- Canvas Layouts Table
CREATE TABLE canvas_layouts (
    case_id UUID PRIMARY KEY REFERENCES cases(id) ON DELETE CASCADE,
    nodes JSONB NOT NULL DEFAULT '{}',
    zoom FLOAT NOT NULL DEFAULT 1.0,
    pan JSONB NOT NULL DEFAULT '{"x": 0, "y": 0}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID NOT NULL REFERENCES auth.users(id),
    CONSTRAINT valid_pan CHECK (
        pan ? 'x' AND 
        pan ? 'y' AND 
        jsonb_typeof(pan->'x') = 'number' AND 
        jsonb_typeof(pan->'y') = 'number'
    )
);

-- Indexes
CREATE INDEX idx_canvas_nodes_case_id ON canvas_nodes(case_id);
CREATE INDEX idx_canvas_edges_case_id ON canvas_edges(case_id);
CREATE INDEX idx_canvas_edges_source ON canvas_edges(source_id);
CREATE INDEX idx_canvas_edges_target ON canvas_edges(target_id);

-- RLS Policies
ALTER TABLE canvas_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE canvas_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE canvas_layouts ENABLE ROW LEVEL SECURITY;

-- Policy for canvas_nodes
CREATE POLICY "Users can view nodes of their cases" ON canvas_nodes
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM cases c
            WHERE c.id = canvas_nodes.case_id
            AND (c.created_by = auth.uid() OR auth.uid() = ANY(c.shared_with))
        )
    );

CREATE POLICY "Users can create nodes in their cases" ON canvas_nodes
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM cases c
            WHERE c.id = canvas_nodes.case_id
            AND (c.created_by = auth.uid() OR auth.uid() = ANY(c.shared_with))
        )
    );

-- Similar policies for edges and layouts
CREATE POLICY "Users can view edges of their cases" ON canvas_edges
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM cases c
            WHERE c.id = canvas_edges.case_id
            AND (c.created_by = auth.uid() OR auth.uid() = ANY(c.shared_with))
        )
    );

CREATE POLICY "Users can create edges in their cases" ON canvas_edges
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM cases c
            WHERE c.id = canvas_edges.case_id
            AND (c.created_by = auth.uid() OR auth.uid() = ANY(c.shared_with))
        )
    );

CREATE POLICY "Users can manage layouts of their cases" ON canvas_layouts
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM cases c
            WHERE c.id = canvas_layouts.case_id
            AND (c.created_by = auth.uid() OR auth.uid() = ANY(c.shared_with))
        )
    );
