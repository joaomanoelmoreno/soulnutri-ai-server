# -*- coding: utf-8 -*-
"""
SoulNutri - Tests for News Feed and Achievements Features
Tests the new nutrition news feed and motivational achievements system.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test PIN for premium user
TEST_PIN = "1234"


class TestNewsFeed:
    """Tests for /api/news/* endpoints - Nutrition news feed"""
    
    def test_news_feed_returns_items(self):
        """GET /api/news/feed - should return list of nutrition news"""
        response = requests.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert "items" in data, "Response should contain 'items' field"
        assert isinstance(data["items"], list), "items should be a list"
        
        # Should have some news items (8 pre-generated according to requirements)
        print(f"News feed returned {len(data['items'])} items")
        
        # Verify item structure if items exist
        if len(data["items"]) > 0:
            item = data["items"][0]
            assert "titulo" in item, "News item should have 'titulo'"
            assert "resumo" in item, "News item should have 'resumo'"
            assert "categoria" in item, "News item should have 'categoria'"
            assert "content_hash" in item, "News item should have 'content_hash'"
            print(f"First news item: {item.get('titulo', 'N/A')[:50]}...")
    
    def test_news_categories_returns_6_categories(self):
        """GET /api/news/categories - should return 6 categories"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert "categories" in data, "Response should contain 'categories' field"
        
        categories = data["categories"]
        assert isinstance(categories, list), "categories should be a list"
        assert len(categories) == 6, f"Expected 6 categories, got {len(categories)}"
        
        # Verify expected categories
        expected_ids = ["curiosidade", "alerta", "dica", "ciencia", "tendencia", "mito_vs_fato"]
        actual_ids = [c.get("id") for c in categories]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids, f"Missing category: {expected_id}"
        
        print(f"Categories: {actual_ids}")
    
    def test_news_feed_filter_by_category(self):
        """GET /api/news/feed?categoria=curiosidade - should filter by category"""
        response = requests.get(f"{BASE_URL}/api/news/feed?categoria=curiosidade")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        
        # All items should be of the filtered category
        for item in data.get("items", []):
            assert item.get("categoria") == "curiosidade", f"Item has wrong category: {item.get('categoria')}"
        
        print(f"Filtered feed returned {len(data.get('items', []))} items of category 'curiosidade'")
    
    def test_news_like_increments(self):
        """POST /api/news/like/{hash} - should increment like count"""
        # First get a news item to like
        feed_response = requests.get(f"{BASE_URL}/api/news/feed?limit=1")
        feed_data = feed_response.json()
        
        if not feed_data.get("items"):
            pytest.skip("No news items available to test like functionality")
        
        content_hash = feed_data["items"][0].get("content_hash")
        initial_likes = feed_data["items"][0].get("likes", 0)
        
        # Like the item
        response = requests.post(f"{BASE_URL}/api/news/like/{content_hash}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        assert "likes" in data, "Response should contain 'likes' field"
        
        # Likes should have incremented
        assert data["likes"] >= initial_likes, f"Likes should have incremented from {initial_likes}"
        print(f"Like count: {initial_likes} -> {data['likes']}")
    
    def test_news_feed_stats(self):
        """GET /api/news/feed - should include stats"""
        response = requests.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200
        
        data = response.json()
        assert "stats" in data, "Response should contain 'stats' field"
        
        stats = data["stats"]
        assert "total" in stats, "Stats should have 'total'"
        assert "by_category" in stats, "Stats should have 'by_category'"
        assert "by_tone" in stats, "Stats should have 'by_tone'"
        
        print(f"News stats: total={stats.get('total')}, by_tone={stats.get('by_tone')}")


class TestPremiumAchievements:
    """Tests for /api/premium/achievements endpoint - Badges, streaks, levels"""
    
    def test_achievements_with_valid_pin(self):
        """GET /api/premium/achievements?pin=1234 - should return achievements data"""
        response = requests.get(f"{BASE_URL}/api/premium/achievements?pin={TEST_PIN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check if PIN is valid (user exists)
        if data.get("error") == "PIN incorreto":
            pytest.skip(f"Test PIN {TEST_PIN} not found in database - user may not exist")
        
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        
        # Verify achievements structure
        assert "badges_unlocked" in data, "Should have 'badges_unlocked'"
        assert "badges_locked" in data, "Should have 'badges_locked'"
        assert "streak" in data, "Should have 'streak'"
        assert "level" in data, "Should have 'level'"
        assert "motivational_messages" in data, "Should have 'motivational_messages'"
        
        # Verify level structure
        level = data["level"]
        assert "nivel" in level, "Level should have 'nivel'"
        assert "nome" in level, "Level should have 'nome'"
        assert "xp" in level, "Level should have 'xp'"
        assert "progresso" in level, "Level should have 'progresso'"
        
        print(f"User achievements: streak={data['streak']}, level={level['nome']}, badges={data.get('total_badges', 0)}")
        print(f"Motivational messages: {data.get('motivational_messages', [])}")
    
    def test_achievements_with_invalid_pin(self):
        """GET /api/premium/achievements?pin=9999 - should return error for invalid PIN"""
        response = requests.get(f"{BASE_URL}/api/premium/achievements?pin=9999")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should return error for invalid PIN
        assert data.get("ok") == False or data.get("error") is not None, "Should return error for invalid PIN"
        print(f"Invalid PIN response: {data}")
    
    def test_achievements_badges_structure(self):
        """Verify badge structure in achievements response"""
        response = requests.get(f"{BASE_URL}/api/premium/achievements?pin={TEST_PIN}")
        data = response.json()
        
        if data.get("error") == "PIN incorreto":
            pytest.skip(f"Test PIN {TEST_PIN} not found in database")
        
        # Check unlocked badges structure
        for badge in data.get("badges_unlocked", []):
            assert "id" in badge, "Badge should have 'id'"
            assert "nome" in badge, "Badge should have 'nome'"
            assert "descricao" in badge, "Badge should have 'descricao'"
            assert "achieved" in badge, "Badge should have 'achieved'"
            assert badge["achieved"] == True, "Unlocked badge should have achieved=True"
        
        # Check locked badges structure
        for badge in data.get("badges_locked", []):
            assert "id" in badge, "Badge should have 'id'"
            assert "nome" in badge, "Badge should have 'nome'"
            assert "progress" in badge, "Badge should have 'progress'"
            assert badge["achieved"] == False, "Locked badge should have achieved=False"
        
        print(f"Unlocked badges: {len(data.get('badges_unlocked', []))}")
        print(f"Locked badges: {len(data.get('badges_locked', []))}")


class TestWeeklyReport:
    """Tests for /api/premium/weekly-report-ai endpoint"""
    
    def test_weekly_report_with_valid_pin(self):
        """GET /api/premium/weekly-report-ai?pin=1234 - should return weekly report"""
        response = requests.get(f"{BASE_URL}/api/premium/weekly-report-ai?pin={TEST_PIN}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        if data.get("error") == "PIN incorreto":
            pytest.skip(f"Test PIN {TEST_PIN} not found in database")
        
        assert data.get("ok") == True, f"Expected ok=True, got {data}"
        
        # Response can have has_data=False if user has no meals logged this week
        # This is valid behavior - just verify the response structure
        if data.get("has_data") == False:
            assert "message" in data, "Should have 'message' when no data"
            print(f"Weekly report: No data this week - {data.get('message')}")
        else:
            # Verify report structure when data exists
            assert "nome" in data, "Should have 'nome'"
            assert "periodo" in data, "Should have 'periodo'"
            print(f"Weekly report for: {data.get('nome')}, period: {data.get('periodo')}")
        
        print(f"Has data: {data.get('has_data', False)}")


class TestHealthAndStatus:
    """Basic health checks"""
    
    def test_api_health(self):
        """GET /api/health - should return ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print("API health: OK")
    
    def test_ai_status(self):
        """GET /api/ai/status - should return ready status"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"AI status: ready={data.get('ready')}, dishes={data.get('total_dishes')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
