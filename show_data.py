import psycopg2
from psycopg2.extras import DictCursor

# Connexion à la base de données
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="videochat",
    user="postgres",
    password="postgres"
)

# Création d'un curseur
cur = conn.cursor(cursor_factory=DictCursor)

# Exécution de la requête
cur.execute("""
    SELECT 
        h.timestamp::int as time,
        h.description,
        h.summary
    FROM highlights h
    ORDER BY h.timestamp;
""")

# Affichage des résultats
print("\nHighlights trouvés dans la vidéo :\n")
print("-" * 80)
for row in cur.fetchall():
    print(f"\nTemps: {row['time']} secondes")
    print(f"Description: {row['description']}")
    if row['summary']:
        print(f"Résumé: {row['summary']}")
    print("-" * 80)

# Fermeture de la connexion
cur.close()
conn.close() 