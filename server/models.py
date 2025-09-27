from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Naming convention for migrations
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# ------------------- User Model -------------------
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=True, default="")
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationship to recipes
    recipes = db.relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    recipe_titles = association_proxy("recipes", "title")

    serialize_rules = ("-recipes.user",)

    # Password property: write-only
    @property
    def password_hash(self):
        raise AttributeError("Password hashes are not readable.")  # ❌ read not allowed

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)  # ✅ hash when set

    # Method to authenticate user
    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

# ------------------- Recipe Model -------------------
class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    
    # ForeignKey to user (nullable allowed)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", back_populates="recipes")

    serialize_rules = ("-user.recipes",)
