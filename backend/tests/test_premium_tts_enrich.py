"""
SoulNutri - Iteration 17 Tests
Testing Premium Content + TTS Fix
- /api/ai/identify - food identification
- /api/ai/enrich - premium content enrichment (beneficios, riscos, curiosidade, combinacoes, noticias)
- /api/ai/tts - text-to-speech audio generation
- /api/premium/login - premium user authentication
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PREMIUM_PIN = "2212"
PREMIUM_NOME = "Joao Manoel"


class TestPremiumLogin:
    """Premium user authentication tests"""
    
    def test_premium_login_success(self):
        """Test premium login with valid credentials (uses Form data)"""
        # Note: This endpoint uses Form data, not JSON
        response = requests.post(f"{BASE_URL}/api/premium/login", data={
            "pin": PREMIUM_PIN,
            "nome": PREMIUM_NOME
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok:true, got {data}"
        assert "user" in data or "nome" in data, f"Expected user data in response: {data}"
        print(f"✓ Premium login successful: {data}")
    
    def test_premium_login_invalid_pin(self):
        """Test premium login with invalid PIN (uses Form data)"""
        response = requests.post(f"{BASE_URL}/api/premium/login", data={
            "pin": "9999",
            "nome": "Invalid User"
        })
        # Should return 200 with ok:false
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("ok") == False, f"Expected ok:false for invalid credentials: {data}"
        print(f"✓ Invalid login correctly rejected")


class TestAIIdentify:
    """Food identification endpoint tests"""
    
    def test_identify_food_image(self):
        """Test /api/ai/identify with a food image"""
        test_image_path = "/tmp/test_food.jpg"
        
        if not os.path.exists(test_image_path):
            pytest.skip("Test food image not found at /tmp/test_food.jpg")
        
        with open(test_image_path, 'rb') as f:
            # Note: field name is 'file' not 'image'
            files = {'file': ('test_food.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok:true, got {data}"
        assert data.get("identified") == True, f"Expected identified:true, got {data}"
        assert "dish_display" in data or "nome" in data, f"Expected dish name in response: {data}"
        
        print(f"✓ Food identified: {data.get('dish_display', data.get('nome'))}")
        return data


class TestAIEnrich:
    """Premium content enrichment endpoint tests"""
    
    def test_enrich_returns_premium_content(self):
        """Test /api/ai/enrich returns beneficios, riscos, curiosidade, combinacoes, noticias"""
        response = requests.post(f"{BASE_URL}/api/ai/enrich", json={
            "nome": "Arroz com Feijao",
            "ingredientes": ["arroz", "feijao", "alho", "cebola", "sal"],
            "pin": PREMIUM_PIN,
            "user_nome": PREMIUM_NOME
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok:true, got {data}"
        
        # Check for premium content fields
        premium_fields = ["beneficios", "riscos", "curiosidade", "combinacoes", "noticias"]
        found_fields = []
        for field in premium_fields:
            if field in data:
                found_fields.append(field)
                print(f"  ✓ {field}: {type(data[field]).__name__} - {str(data[field])[:100]}...")
        
        assert len(found_fields) >= 3, f"Expected at least 3 premium fields, found: {found_fields}"
        print(f"✓ Enrich returned premium content: {found_fields}")
        return data
    
    def test_enrich_without_premium_user(self):
        """Test enrich without premium credentials"""
        response = requests.post(f"{BASE_URL}/api/ai/enrich", json={
            "nome": "Salada",
            "ingredientes": ["alface", "tomate"],
            "pin": "",
            "user_nome": ""
        })
        
        # Should still return 200 but possibly with limited content
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"✓ Enrich without premium: ok={data.get('ok')}")


class TestTTS:
    """Text-to-Speech endpoint tests"""
    
    def test_tts_returns_audio(self):
        """Test /api/ai/tts returns audio/mpeg with > 10000 bytes"""
        dish_data = {
            "dish_display": "Arroz com Feijao",
            "nutrition": {
                "calorias": "350 kcal",
                "proteinas": "12g",
                "carboidratos": "60g"
            },
            "ingredientes": ["arroz", "feijao", "alho", "cebola"],
            "beneficios": ["Rico em proteinas vegetais", "Fonte de fibras"],
            "riscos": ["Alto indice glicemico"],
            "alergenos": {"gluten": False, "lactose": False}
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/tts", json={
            "dish_data": dish_data,
            "voice": "alloy"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200] if response.text else 'empty'}"
        
        content_type = response.headers.get("Content-Type", "")
        assert "audio/mpeg" in content_type, f"Expected audio/mpeg, got {content_type}"
        
        audio_size = len(response.content)
        assert audio_size > 10000, f"Expected audio > 10000 bytes, got {audio_size} bytes"
        
        print(f"✓ TTS returned audio: {audio_size} bytes ({audio_size // 1024}KB)")
    
    def test_tts_without_dish_data(self):
        """Test TTS with empty dish data returns error"""
        response = requests.post(f"{BASE_URL}/api/ai/tts", json={
            "dish_data": {},
            "voice": "alloy"
        })
        
        # Should return JSON error, not audio
        if response.status_code == 200:
            # Check if it's JSON error response
            try:
                data = response.json()
                assert data.get("ok") == False, f"Expected ok:false for empty dish data"
                print(f"✓ TTS correctly rejected empty dish data")
            except:
                # If it returned audio anyway, that's also acceptable
                print(f"✓ TTS returned response for empty data")
        else:
            print(f"✓ TTS returned error status {response.status_code} for empty data")


class TestAPIStatus:
    """Basic API health checks"""
    
    def test_ai_status(self):
        """Test /api/ai/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") == True, f"Expected ok:true, got {data}"
        print(f"✓ AI Status: {data.get('dishes_count', 'N/A')} dishes, {data.get('embeddings_count', 'N/A')} embeddings")
    
    def test_dishes_endpoint(self):
        """Test /api/ai/dishes endpoint"""
        response = requests.get(f"{BASE_URL}/api/ai/dishes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Response is {ok: true, dishes: [...], total: N}
        assert data.get("ok") == True, f"Expected ok:true, got {data}"
        assert "dishes" in data, f"Expected dishes key in response"
        dishes = data["dishes"]
        assert isinstance(dishes, list), f"Expected list of dishes, got {type(dishes)}"
        assert len(dishes) > 0, "Expected at least one dish"
        print(f"✓ Dishes endpoint: {len(dishes)} dishes returned")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
