-- Gaming Data Pipeline Database Schema
-- Supports both PostgreSQL and DuckDB

-- Games Table
CREATE TABLE IF NOT EXISTS games (
    game_id VARCHAR(50) PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    platform VARCHAR(50),
    genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players Table
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(100),
    game_id VARCHAR(50),
    platform_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

-- Matches Table
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(100) PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    match_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    match_type VARCHAR(50),
    platform VARCHAR(50),
    source VARCHAR(50),
    additional_data JSON,  -- For game-specific fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

-- Player Stats Table
CREATE TABLE IF NOT EXISTS player_stats (
    stat_id VARCHAR(100) PRIMARY KEY,
    player_id VARCHAR(100) NOT NULL,
    match_id VARCHAR(100) NOT NULL,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    rank INTEGER,
    additional_stats JSON,  -- For game-specific stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Game Events Table
CREATE TABLE IF NOT EXISTS game_events (
    event_id VARCHAR(100) PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL,
    game_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    event_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

-- Forecasts Table
CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id VARCHAR(100) PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_metric VARCHAR(100) NOT NULL,
    predicted_value DECIMAL(15, 2),
    confidence_interval_lower DECIMAL(15, 2),
    confidence_interval_upper DECIMAL(15, 2),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_matches_game_id ON matches(game_id);
CREATE INDEX IF NOT EXISTS idx_matches_match_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_match_id ON player_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_game_events_match_id ON game_events(match_id);
CREATE INDEX IF NOT EXISTS idx_game_events_event_timestamp ON game_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_forecasts_game_id ON forecasts(game_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_date ON forecasts(forecast_date);

-- Initial game data
INSERT OR IGNORE INTO games (game_id, game_name, platform, genre) VALUES
    ('dota2', 'Dota 2', 'steam', 'MOBA'),
    ('csgo', 'Counter-Strike: Global Offensive', 'steam', 'FPS'),
    ('valorant', 'Valorant', 'riot', 'FPS'),
    ('gta5', 'Grand Theft Auto V', 'steam', 'Action'),
    ('pubg', 'PlayerUnknown''s Battlegrounds', 'steam', 'Battle Royale'),
    ('cod', 'Call of Duty', 'activision', 'FPS');
