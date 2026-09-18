from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_order_id", sa.String(64), nullable=False),
        sa.Column("exchange_order_id", sa.String(128), nullable=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("quantity", sa.Numeric(30, 12), nullable=False),
        sa.Column("price", sa.Numeric(30, 12), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_orders_client_order_id", "orders", ["client_order_id"], unique=True)
    op.create_index("ix_orders_exchange_order_id", "orders", ["exchange_order_id"])
    op.create_index("ix_orders_symbol", "orders", ["symbol"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "fills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_trade_id", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("quantity", sa.Numeric(30, 12), nullable=False),
        sa.Column("price", sa.Numeric(30, 12), nullable=False),
        sa.Column("fee", sa.Numeric(30, 12), nullable=False, server_default="0"),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fills_exchange_trade_id", "fills", ["exchange_trade_id"], unique=True)
    op.create_index("ix_fills_symbol", "fills", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_fills_symbol", table_name="fills")
    op.drop_index("ix_fills_exchange_trade_id", table_name="fills")
    op.drop_table("fills")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_symbol", table_name="orders")
    op.drop_index("ix_orders_exchange_order_id", table_name="orders")
    op.drop_index("ix_orders_client_order_id", table_name="orders")
    op.drop_table("orders")
