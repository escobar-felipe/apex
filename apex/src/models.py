from src.ext.database import db
from flask_login import UserMixin
from src.utils.security import decrypt_secret, encrypt_secret


class Tenant(db.Model):
    __tablename__ = "tenant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    domain = db.Column(db.String(255), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True)
    users = db.relationship("User", backref="tenant")
    searchresults = db.relationship("SearchResult", backref="tenant")
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return '<Tenant %r>' % self.slug


class User(UserMixin, db.Model):
    __tablename__ = "user"
    __table_args__ = (
        db.UniqueConstraint("tenant_id", "username", name="uq_user_tenant_username"),
        db.Index("ix_user_tenant_admin", "tenant_id", "admin"),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=True, index=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(512))
    _api_key = db.Column("api_key", db.String(2048), default=None)
    _serpapi_key = db.Column("serpapi_key", db.String(2048), default=None)
    email = db.Column(db.String(512), default=None)
    _stmp_password = db.Column("stmp_password", db.String(2048), default=None)
    admin = db.Column(db.Boolean, default=False)
    rearchresults = db.relationship('SearchResult', backref='user')
    created_at = db.Column(db.DateTime, default=db.func.now())

    @property
    def api_key(self):
        return decrypt_secret(self._api_key)

    @api_key.setter
    def api_key(self, value):
        self._api_key = encrypt_secret(value)

    @property
    def serpapi_key(self):
        return decrypt_secret(self._serpapi_key)

    @serpapi_key.setter
    def serpapi_key(self, value):
        self._serpapi_key = encrypt_secret(value)

    @property
    def stmp_password(self):
        return decrypt_secret(self._stmp_password)

    @stmp_password.setter
    def stmp_password(self, value):
        self._stmp_password = encrypt_secret(value)

    def __repr__(self):
        return '<User %r>' % self.username
    
    
class SearchResult(db.Model):
    __tablename__ = 'searchresults'
    __table_args__ = (
        db.Index("ix_searchresults_user_created_at", "user_id", "created_at"),
        db.Index("ix_searchresults_tenant_created_at", "tenant_id", "created_at"),
        db.Index("ix_searchresults_result_id", "result_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=True, index=True)
    title = db.Column(db.String(512))
    result_id = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(40), default="generating", nullable=False)
    report_type = db.Column(db.String(80), default="monitoring")
    audience = db.Column(db.String(160), nullable=True)
    objective = db.Column(db.String(512), nullable=True)
    tone = db.Column(db.String(80), default="executive")
    report_data = db.Column(db.JSON, nullable=True)
    report_html = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())


class SearchAudit(db.Model):
    __tablename__ = "search_audit"
    __table_args__ = (
        db.Index("ix_search_audit_tenant_created_at", "tenant_id", "created_at"),
        db.Index("ix_search_audit_user_created_at", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    search_query = db.Column("query", db.String(512), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    provider = db.Column(db.String(80), default="serper")
    result_counts = db.Column(db.JSON, nullable=True)
    error_message = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())


class EmailAudit(db.Model):
    __tablename__ = "email_audit"
    __table_args__ = (
        db.Index("ix_email_audit_tenant_created_at", "tenant_id", "created_at"),
        db.Index("ix_email_audit_user_created_at", "user_id", "created_at"),
        db.Index("ix_email_audit_search_result_created_at", "search_result_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    search_result_id = db.Column(db.Integer, db.ForeignKey("searchresults.id"), nullable=True, index=True)
    celery_task_id = db.Column(db.String(512), nullable=True, index=True)
    recipient = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    error_message = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
