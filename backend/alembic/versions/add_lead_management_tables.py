"""Add lead management tables

Revision ID: add_lead_management
Revises: 
Create Date: 2025-08-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_lead_management'
down_revision = '143b6c1aefc8'
branch_labels = None
depends_on = None


def upgrade():
    # Create leads table (simplified without foreign keys to non-existent tables)
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        
        # Contact Information
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=True),
        
        # Lead Scoring
        sa.Column('lead_score', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('score_category', sa.String(20), nullable=False, server_default='warm'),
        sa.Column('score_reasons', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Status & Tracking
        sa.Column('status', sa.String(50), nullable=False, server_default='new'),
        sa.Column('source', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Dates
        sa.Column('first_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('conversion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lost_reason', sa.String(255), nullable=True),
        
        # Financial
        sa.Column('conversion_value', sa.Float(), nullable=True),
        sa.Column('lifetime_value', sa.Float(), nullable=True),
        
        # Enrichment Data
        sa.Column('enrichment_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('enriched_at', sa.DateTime(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
        # Foreign keys removed - will be added later when tables exist
    )
    
    # Create indexes for leads
    op.create_index('ix_leads_organization_id', 'leads', ['organization_id'])
    op.create_index('ix_leads_phone', 'leads', ['phone'])
    op.create_index('ix_leads_email', 'leads', ['email'])
    op.create_index('ix_leads_status', 'leads', ['status'])
    op.create_index('ix_leads_score_category', 'leads', ['score_category'])
    op.create_index('ix_leads_lead_score', 'leads', ['lead_score'])
    op.create_index('ix_leads_last_contact_date', 'leads', ['last_contact_date'])
    
    # Create lead_activities table (simplified)
    op.create_table(
        'lead_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes for lead_activities
    op.create_index('ix_lead_activities_lead_id', 'lead_activities', ['lead_id'])
    op.create_index('ix_lead_activities_activity_type', 'lead_activities', ['activity_type'])
    op.create_index('ix_lead_activities_created_at', 'lead_activities', ['created_at'])
    
    # Create follow_ups table (simplified)
    op.create_table(
        'follow_ups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('follow_up_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('script_type', sa.String(50), nullable=False, server_default='standard'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('outcome', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    
    # Create indexes for follow_ups
    op.create_index('ix_follow_ups_lead_id', 'follow_ups', ['lead_id'])
    op.create_index('ix_follow_ups_scheduled_date', 'follow_ups', ['scheduled_date'])
    op.create_index('ix_follow_ups_status', 'follow_ups', ['status'])
    op.create_index('ix_follow_ups_priority', 'follow_ups', ['priority'])
    
    # Skip adding columns to other tables that might not exist
    pass


def downgrade():
    # Drop indexes and tables in reverse order
    try:
        op.drop_index('ix_organizations_subscription_plan', 'organizations')
        op.drop_column('organizations', 'subscription_plan')
    except:
        pass
    
    try:
        op.drop_index('ix_call_logs_lead_id', 'call_logs')
        op.drop_constraint('fk_call_logs_lead_id', 'call_logs', type_='foreignkey')
        op.drop_column('call_logs', 'lead_score_after')
        op.drop_column('call_logs', 'lead_score_before')
        op.drop_column('call_logs', 'lead_id')
    except:
        pass
    
    # Drop follow_ups
    op.drop_index('ix_follow_ups_priority', 'follow_ups')
    op.drop_index('ix_follow_ups_status', 'follow_ups')
    op.drop_index('ix_follow_ups_scheduled_date', 'follow_ups')
    op.drop_index('ix_follow_ups_lead_id', 'follow_ups')
    op.drop_table('follow_ups')
    
    # Drop lead_activities
    op.drop_index('ix_lead_activities_created_at', 'lead_activities')
    op.drop_index('ix_lead_activities_activity_type', 'lead_activities')
    op.drop_index('ix_lead_activities_lead_id', 'lead_activities')
    op.drop_table('lead_activities')
    
    # Drop leads
    op.drop_index('ix_leads_last_contact_date', 'leads')
    op.drop_index('ix_leads_lead_score', 'leads')
    op.drop_index('ix_leads_score_category', 'leads')
    op.drop_index('ix_leads_status', 'leads')
    op.drop_index('ix_leads_email', 'leads')
    op.drop_index('ix_leads_phone', 'leads')
    op.drop_index('ix_leads_organization_id', 'leads')
    op.drop_table('leads')