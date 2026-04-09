"""
SoulNutri Premium Features Test Suite
=====================================
Tests for P0 bug fix: Premium features (ingredientes, riscos, benefícios, alertas, 
notícias, curiosidades, combinações) should show in the UI after adding a dish.

Test Credentials:
- Premium User: pin=1234, nome=Teste SoulNutri
- Admin: joaomanoelmoreno / Pqlamz0192
"""

import pytest
import requests
import os
import time

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://geofence-analysis.preview.emergentagent.com"

print(f"[TEST] Using BASE_URL: {BASE_URL}")


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ API Health: {data}")
    
    def test_ai_status(self):
        """Test AI status endpoint"""
        response = requests.get(f"{BASE_URL}/api/ai/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert data.get("ready") == True
        print(f"✅ AI Status: ready={data.get('ready')}, dishes={data.get('total_dishes')}")


class TestPremiumIdentifyExternal:
    """
    Test POST /api/ai/identify with restaurant=externo (Gemini Flash mode)
    Premium user should receive rich nutrition data including:
    - ingredientes, beneficios, riscos, curiosidade, combinacoes
    """
    
    def test_identify_external_premium_user(self):
        """
        Test identify endpoint with premium user credentials (pin=1234, nome=Teste SoulNutri)
        Should return is_premium=true and premium fields populated
        """
        # Use test food image
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found at /tmp/test_food_real.jpg")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "externo",
                "pin": "1234",
                "nome": "Teste SoulNutri",
                "country": "BR"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        result = response.json()
        
        # Basic assertions
        assert result.get("ok") == True, f"Expected ok=True, got {result}"
        assert result.get("identified") == True, f"Expected identified=True, got {result}"
        
        # Premium user assertion
        assert result.get("is_premium") == True, f"Expected is_premium=True for pin=1234, got {result.get('is_premium')}"
        
        # Source should be gemini_flash for external mode
        assert result.get("source") == "gemini_flash", f"Expected source=gemini_flash, got {result.get('source')}"
        
        print(f"✅ Identify External Premium: dish={result.get('dish_display')}, is_premium={result.get('is_premium')}, source={result.get('source')}")
        
        # Check premium fields are populated
        # These fields should come from Gemini Flash response
        ingredientes = result.get("ingredientes", [])
        beneficios = result.get("beneficios", [])
        riscos = result.get("riscos", [])
        curiosidade = result.get("curiosidade", "")
        combinacoes = result.get("combinacoes", [])
        
        print(f"  - ingredientes: {ingredientes}")
        print(f"  - beneficios: {beneficios}")
        print(f"  - riscos: {riscos}")
        print(f"  - curiosidade: {curiosidade[:100] if curiosidade else 'N/A'}...")
        print(f"  - combinacoes: {combinacoes}")
        
        # At least some premium fields should be populated
        has_premium_data = (
            len(ingredientes) > 0 or 
            len(beneficios) > 0 or 
            len(riscos) > 0 or 
            curiosidade or 
            len(combinacoes) > 0
        )
        assert has_premium_data, "Expected at least some premium fields (ingredientes, beneficios, riscos, curiosidade, combinacoes) to be populated"
        
        # Check scientific data for premium users
        beneficio_principal = result.get("beneficio_principal")
        curiosidade_cientifica = result.get("curiosidade_cientifica")
        
        print(f"  - beneficio_principal: {beneficio_principal}")
        print(f"  - curiosidade_cientifica: {curiosidade_cientifica}")
        
        return result
    
    def test_identify_external_non_premium_user(self):
        """
        Test identify endpoint without premium credentials
        Should return is_premium=false
        """
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "externo",
                "country": "BR"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result.get("ok") == True
        assert result.get("is_premium") == False, f"Expected is_premium=False without credentials, got {result.get('is_premium')}"
        
        print(f"✅ Identify External Non-Premium: dish={result.get('dish_display')}, is_premium={result.get('is_premium')}")
        
        return result


class TestCibiSanaMode:
    """
    Test POST /api/ai/identify with restaurant=cibi_sana (CLIP local mode)
    Should use local CLIP index, not Gemini
    """
    
    def test_identify_cibi_sana_uses_clip(self):
        """
        Test that cibi_sana mode uses CLIP local index (source=local_index)
        """
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "cibi_sana",
                "pin": "1234",
                "nome": "Teste SoulNutri",
                "country": "BR"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # For cibi_sana, source should be local_index (CLIP)
        source = result.get("source")
        assert source == "local_index", f"Expected source=local_index for cibi_sana, got {source}"
        
        print(f"✅ Identify Cibi Sana: dish={result.get('dish_display')}, source={source}")
        
        return result


class TestPremiumLogin:
    """Test Premium user login endpoint"""
    
    def test_premium_login_valid_credentials(self):
        """Test login with valid premium credentials"""
        data = {
            "pin": "1234",
            "nome": "Teste SoulNutri"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data=data,
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result.get("ok") == True, f"Expected ok=True for valid credentials, got {result}"
        assert "user" in result, f"Expected user object in response, got {result}"
        
        user = result.get("user", {})
        assert user.get("nome") == "Teste SoulNutri", f"Expected nome='Teste SoulNutri', got {user.get('nome')}"
        
        print(f"✅ Premium Login: user={user.get('nome')}, ok={result.get('ok')}")
        
        return result
    
    def test_premium_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            "pin": "9999",
            "nome": "Invalid User"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data=data,
            timeout=10
        )
        
        # Should return 200 but ok=False or 401/404
        result = response.json()
        
        # Either ok=False or error response
        if response.status_code == 200:
            assert result.get("ok") == False, f"Expected ok=False for invalid credentials"
        else:
            assert response.status_code in [401, 404], f"Expected 401/404 for invalid credentials, got {response.status_code}"
        
        print(f"✅ Premium Login Invalid: status={response.status_code}, ok={result.get('ok')}")


class TestGeminiFlashService:
    """Test Gemini Flash service availability"""
    
    def test_gemini_flash_status(self):
        """Test Gemini Flash status endpoint"""
        response = requests.get(f"{BASE_URL}/api/ai/flash-status", timeout=10)
        
        assert response.status_code == 200
        result = response.json()
        
        # Check if Gemini Flash is available
        available = result.get("available", False)
        print(f"✅ Gemini Flash Status: available={available}, model={result.get('model')}")
        
        return result


class TestPremiumFieldsMapping:
    """
    Verify that premium fields from Gemini Flash are correctly mapped through the stack
    """
    
    def test_premium_fields_in_response(self):
        """
        Comprehensive test for all premium fields in identify response
        """
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "externo",
                "pin": "1234",
                "nome": "Teste SoulNutri",
                "country": "BR"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # List of expected premium fields
        premium_fields = [
            "ingredientes",
            "beneficios", 
            "riscos",
            "curiosidade",
            "combinacoes",
            "beneficio_principal",
            "curiosidade_cientifica",
            "alerta_saude",
            "mito_verdade",
            "is_premium"
        ]
        
        print("\n📋 Premium Fields Check:")
        fields_present = {}
        for field in premium_fields:
            value = result.get(field)
            is_present = value is not None and (
                (isinstance(value, list) and len(value) > 0) or
                (isinstance(value, str) and len(value) > 0) or
                (isinstance(value, bool)) or
                (isinstance(value, dict) and len(value) > 0)
            )
            fields_present[field] = is_present
            status = "✅" if is_present else "❌"
            print(f"  {status} {field}: {type(value).__name__} = {str(value)[:80] if value else 'None'}...")
        
        # Critical assertions
        assert result.get("is_premium") == True, "is_premium should be True"
        
        # At least ingredientes, beneficios, or riscos should be populated from Gemini
        gemini_fields_populated = (
            fields_present.get("ingredientes") or
            fields_present.get("beneficios") or
            fields_present.get("riscos")
        )
        assert gemini_fields_populated, "At least one of ingredientes/beneficios/riscos should be populated from Gemini"
        
        print(f"\n✅ Premium Fields Test Complete: {sum(fields_present.values())}/{len(premium_fields)} fields populated")
        
        return result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
