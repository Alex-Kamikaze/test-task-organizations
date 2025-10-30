"""Обновил поля address, latitude и longitude у Building

Revision ID: 04c2b95278e9
Revises: c8fc346e8537
Create Date: 2025-10-24 02:01:22.328331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04c2b95278e9'
down_revision: Union[str, Sequence[str], None] = 'c8fc346e8537'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Для PostgreSQL нужно явно указать преобразование типа
    op.alter_column('buildings', 'latitude',
               type_=sa.Float(),
               postgresql_using='latitude::double precision')
    
    op.alter_column('buildings', 'longitude',
               type_=sa.Float(),
               postgresql_using='longitude::double precision')
    
    # Если есть другие изменения, оставьте их здесь

def downgrade():
    # Аналогично для отката
    op.alter_column('buildings', 'longitude',
               type_=sa.String(),
               postgresql_using='longitude::text')
    
    op.alter_column('buildings', 'latitude',
               type_=sa.String(),
               postgresql_using='latitude::text')
