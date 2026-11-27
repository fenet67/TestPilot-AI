"""Service layer.

Services own business logic and storage. Routes call them; they never import
FastAPI request objects. Day 6 replaces the in-memory session store with the
database without changing this boundary.
"""
