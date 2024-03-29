"""change_collation_for_emojis

Revision ID: 0c29662d1bf0
Revises: 9b20743f3e4a
Create Date: 2023-02-04 13:37:02.289026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import String

from discorss_models.models import MAX_STRING_SIZE

revision = '0c29662d1bf0'
down_revision = '9b20743f3e4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("link", "title", nullable=False, type_=String(MAX_STRING_SIZE, collation="utf8mb4_general_ci"))
    op.alter_column("discord_server", "name", unique=False, nullable=False, type_=String(MAX_STRING_SIZE, collation="utf8mb4_general_ci"))
    op.alter_column("discord_server_channel", "name", unique=False, nullable=False, type_=String(MAX_STRING_SIZE, collation="utf8mb4_general_ci"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("link", "title", nullable=False, type_=String(MAX_STRING_SIZE))
    op.alter_column("discord_server", "name", unique=False, nullable=False, type_=String(MAX_STRING_SIZE))
    op.alter_column("discord_server_channel", "name", nullable=False, type_=String(MAX_STRING_SIZE))
    # ### end Alembic commands ###
