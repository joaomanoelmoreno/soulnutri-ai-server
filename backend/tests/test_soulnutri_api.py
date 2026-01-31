"""
SoulNutri API Tests - Backend Testing
Tests for /api/ai/identify and related endpoints
"""
import pytest
import requests
import os
from pathlib import Path

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test image path
TEST_IMAGE_PATH = "/app/datasets/organized/aboboraaocurry/aboboraaocurry.jpeg"
TEST_IMAGE_PATH_2 = "/app/datasets/organized/arrozbranco/arrozbranco.jpeg"


class TestHealthAndStatus:
    """Health check and status endpoints"""
    
    def test_api_status(self):
        """Test /api/ai/status returns ready state"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert data.get("ready") == True
        assert "total_dishes" in data
        assert data["total_dishes"] > 0
        print(f"✓ API Status: {data['total_dishes']} dishes indexed")
    
    def test_api_dishes_list(self):
        """Test /api/ai/dishes returns dish list"""
        response = requests.get(f"{BASE_URL}/api/ai/dishes")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "dishes" in data
        assert len(data["dishes"]) > 0
        # Verify dish structure
        dish = data["dishes"][0]
        assert "slug" in dish
        assert "name" in dish
        print(f"✓ Dishes list: {len(data['dishes'])} dishes available")


class TestImageIdentification:
    """Test /api/ai/identify endpoint - Core functionality"""
    
    def test_identify_single_dish(self):
        """Test identifying a single dish from image"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert data.get("identified") == True
        
        # Verify response structure
        assert "dish" in data  # slug
        assert "dish_display" in data  # display name
        assert "confidence" in data
        assert "score" in data
        
        # Verify nutritional info
        assert "nutrition" in data or "calorias_estimadas" in data
        
        print(f"✓ Identified: {data.get('dish_display')} (confidence: {data.get('confidence')}, score: {data.get('score')})")
    
    def test_identify_returns_category(self):
        """Test that identification returns category info"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Category should be present
        assert "category" in data or "categoria" in data
        category = data.get("category") or data.get("categoria")
        assert category in ["vegano", "vegetariano", "proteína animal", "não classificado"]
        print(f"✓ Category: {category}")
    
    def test_identify_returns_allergens(self):
        """Test that identification returns allergen info"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Allergen info should be present
        assert "contem_gluten" in data or "riscos" in data
        print(f"✓ Allergen info present: gluten={data.get('contem_gluten')}, lactose={data.get('contem_lactose')}")
    
    def test_identify_returns_ingredients(self):
        """Test that identification returns ingredients list"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Ingredients should be present
        assert "ingredientes" in data
        assert isinstance(data["ingredientes"], list)
        print(f"✓ Ingredients: {len(data.get('ingredientes', []))} items")
    
    def test_identify_returns_benefits(self):
        """Test that identification returns benefits list"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Benefits should be present
        assert "beneficios" in data
        assert isinstance(data["beneficios"], list)
        print(f"✓ Benefits: {len(data.get('beneficios', []))} items")
    
    def test_identify_empty_file_error(self):
        """Test error handling for empty file"""
        files = {'file': ('empty.jpg', b'', 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        # Should return error
        assert response.status_code in [200, 400, 422]
        data = response.json()
        # Either ok=False or error message
        if response.status_code == 200:
            assert data.get("ok") == False or data.get("error") is not None
        print(f"✓ Empty file handled correctly")


class TestMultiItemIdentification:
    """Test /api/ai/identify-multi endpoint - Buffet scenario"""
    
    def test_identify_multi_endpoint_exists(self):
        """Test that multi-item endpoint exists"""
        if not os.path.exists(TEST_IMAGE_PATH):
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify-multi", files=files)
        
        assert response.status_code == 200
        data = response.json()
        # Should return some result (ok or error)
        assert "ok" in data or "error" in data
        print(f"✓ Multi-item endpoint working: {data.get('ok', 'error')}")


class TestInternationalization:
    """Test i18n endpoints"""
    
    def test_get_languages(self):
        """Test /api/i18n/languages returns supported languages"""
        response = requests.get(f"{BASE_URL}/api/i18n/languages")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "languages" in data
        print(f"✓ Languages: {len(data.get('languages', []))} supported")
    
    def test_get_ui_translations_pt(self):
        """Test /api/i18n/ui/pt returns Portuguese translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/ui/pt")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "translations" in data
        print(f"✓ PT translations loaded")
    
    def test_get_ui_translations_en(self):
        """Test /api/i18n/ui/en returns English translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/ui/en")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "translations" in data
        print(f"✓ EN translations loaded")


class TestFeedbackEndpoint:
    """Test feedback endpoint"""
    
    def test_feedback_stats(self):
        """Test /api/ai/feedback/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/ai/feedback/stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "total_feedbacks" in data
        print(f"✓ Feedback stats: {data.get('total_feedbacks')} total")


class TestCombinationsEndpoint:
    """Test food combinations endpoint"""
    
    def test_get_combinations(self):
        """Test /api/ai/combinations returns food combinations"""
        response = requests.get(f"{BASE_URL}/api/ai/combinations")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "combinations" in data
        print(f"✓ Combinations: {len(data.get('combinations', []))} available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
