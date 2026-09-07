import psycopg2

try:
    conn = psycopg2.connect('host=localhost user=voice_user password=voice_password dbname=voice_insights')
    cursor = conn.cursor()
    
    print('=== SESSIONS (Latest 5) ===')
    cursor.execute('SELECT id, created_at FROM sessions ORDER BY created_at DESC LIMIT 5')
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, Created: {row[1]}')
    
    print('\n=== INSIGHTS (Latest 5) ===')
    cursor.execute('SELECT session_id, theme, sentiment, actionable FROM insights ORDER BY created_at DESC LIMIT 5')
    for row in cursor.fetchall():
        print(f'Session: {row[0]}, Theme: {row[1]}, Sentiment: {row[2]}, Actionable: {row[3]}')
    
    print('\n=== LLM_CALLS (Latest 5) ===')
    cursor.execute('SELECT session_id, latency_ms, retry_count, input_tokens, output_tokens FROM llm_calls ORDER BY created_at DESC LIMIT 5')
    for row in cursor.fetchall():
        print(f'Session: {row[0]}, Latency: {row[1]}ms, Retries: {row[2]}, In: {row[3]}, Out: {row[4]}')
    
    print('\n=== DATABASE STATS ===')
    cursor.execute('SELECT COUNT(*) FROM sessions')
    print(f'Total sessions: {cursor.fetchone()[0]}')
    cursor.execute('SELECT COUNT(*) FROM insights')
    print(f'Total insights: {cursor.fetchone()[0]}')
    cursor.execute('SELECT COUNT(*) FROM llm_calls')
    print(f'Total LLM calls: {cursor.fetchone()[0]}')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
