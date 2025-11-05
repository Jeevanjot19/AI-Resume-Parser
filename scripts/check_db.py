import sqlite3

conn = sqlite3.connect('data/resume_parser.db')
cursor = conn.cursor()

# Total resumes
cursor.execute('SELECT COUNT(*) FROM resumes')
total = cursor.fetchone()[0]

# Unique file hashes
cursor.execute('SELECT COUNT(DISTINCT file_hash) FROM resumes')
unique_hashes = cursor.fetchone()[0]

# Unique file names
cursor.execute('SELECT COUNT(DISTINCT file_name) FROM resumes')
unique_names = cursor.fetchone()[0]

print("\n" + "="*60)
print("Database Resume Analysis")
print("="*60)
print(f"Total resumes: {total}")
print(f"Unique file hashes: {unique_hashes}")
print(f"Unique file names: {unique_names}")
print(f"\nDuplicates by hash: {total - unique_hashes}")
print(f"Duplicates by name: {total - unique_names}")
print("="*60)

if total == unique_hashes:
    print("\n✓ All resumes are UNIQUE - no duplicates!")
else:
    print(f"\n⚠ Found {total - unique_hashes} duplicate resumes")

# Show sample filenames
cursor.execute('SELECT file_name FROM resumes LIMIT 30')
names = cursor.fetchall()

print(f"\nFirst 30 filenames:")
for i, (name,) in enumerate(names, 1):
    print(f"  {i:2}. {name}")

conn.close()
