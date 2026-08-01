"""complete_schema

Revision ID: 0002_complete_schema
Revises: 0001_initial_schema
Create Date: 2026-08-01 00:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_complete_schema'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'analyses' table
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_doctor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_url', sa.String(length=512), nullable=False),
        sa.Column('lesion_body_location', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_doctor_id'], ['doctors.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_assigned_doctor_id'), 'analyses', ['assigned_doctor_id'], unique=False)
    op.create_index(op.f('ix_analyses_patient_id'), 'analyses', ['patient_id'], unique=False)
    op.create_index(op.f('ix_analyses_status'), 'analyses', ['status'], unique=False)

    # 2. Create 'predictions' table
    op.create_table(
        'predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('predicted_class', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('class_probabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('heatmap_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_analysis_id'), 'predictions', ['analysis_id'], unique=False)

    # 3. Create 'reports' table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pdf_url', sa.String(length=512), nullable=False),
        sa.Column('doctor_notes', sa.Text(), nullable=True),
        sa.Column('severity_level', sa.String(length=32), nullable=False, server_default='LOW'),
        sa.Column('download_token', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_analysis_id'), 'reports', ['analysis_id'], unique=True)
    op.create_index(op.f('ix_reports_download_token'), 'reports', ['download_token'], unique=True)

    # 4. Create 'appointments' table
    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('appointment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='SCHEDULED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_appointment_date'), 'appointments', ['appointment_date'], unique=False)
    op.create_index(op.f('ix_appointments_doctor_id'), 'appointments', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_appointments_patient_id'), 'appointments', ['patient_id'], unique=False)

    # 5. Create 'notifications' table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)

    # 6. Create 'consents' table
    op.create_table(
        'consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consent_type', sa.String(length=64), nullable=False),
        sa.Column('is_granted', sa.Boolean(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_consents_user_id'), 'consents', ['user_id'], unique=False)

    # 7. Create 'refresh_tokens' table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index(op.f('ix_consents_user_id'), table_name='consents')
    op.drop_table('consents')

    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_table('notifications')

    op.drop_index(op.f('ix_appointments_patient_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_doctor_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_appointment_date'), table_name='appointments')
    op.drop_table('appointments')

    op.drop_index(op.f('ix_reports_download_token'), table_name='reports')
    op.drop_index(op.f('ix_reports_analysis_id'), table_name='reports')
    op.drop_table('reports')

    op.drop_index(op.f('ix_predictions_analysis_id'), table_name='predictions')
    op.drop_table('predictions')

    op.drop_index(op.f('ix_analyses_status'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_patient_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_assigned_doctor_id'), table_name='analyses')
    op.drop_table('analyses')
