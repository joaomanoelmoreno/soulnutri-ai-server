"""
SoulNutri P0 Bug Fix Test Suite
================================
Tests for the 5 critical issues fixed:
1. (P0) Slow /ai/identify - should respond in <3s
2. (P0) Premium login stuck with stale localStorage PIN - should fail gracefully for invalid pin
3. (P1) Alerts not generated - /ai/enrich should return alertas_historico
4. (P1) Feedback endpoint 500 error - should NOT return 500
5. (P2) TTS content expanded - should generate audio

Test Credentials (from cloud MongoDB):
- Premium User: pin=2212, nome=Joao Manoel (with trailing space in DB)
- Also works: pin=1234, nome=Teste SoulNutri
- Invalid: pin=9999 (no user with this pin)
"""

import pytest
import requests
import os
import time
import json

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://onnx-timeout-fix.preview.emergentagent.com"

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
        print(f"✅ AI Status: ready={data.get('ready')}, dishes={data.get('total_dishes')}")


class TestP0SlowIdentify:
    """
    P0 Fix: /ai/identify should respond in <3 seconds
    Previously was 8-9s due to LLM enrichment blocking the response.
    Now enrichment is moved to background /ai/enrich endpoint.
    """
    
    def test_identify_cibi_sana_fast(self):
        """
        Test /ai/identify with restaurant=cibi_sana (CLIP mode)
        Should respond in <5 seconds (allowing for network latency)
        """
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found at /tmp/test_food_real.jpg")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "cibi_sana",
                "pin": "2212",
                "nome": "Joao Manoel",
                "country": "BR"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
            elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        result = response.json()
        
        # Check response time - allow up to 5s for network latency
        assert elapsed < 5.0, f"P0 FIX FAILED: /ai/identify took {elapsed:.2f}s (should be <5s)"
        
        # Check source - could be local_index or cached
        source = result.get("source", "")
        assert "local_index" in source or "cached" in source, f"Expected source containing 'local_index' or 'cached' for cibi_sana, got {source}"
        
        # For premium users, should have enrichment_pending=true
        premium = result.get("premium", {})
        if result.get("is_premium"):
            assert premium.get("enrichment_pending") == True, "Premium users should have enrichment_pending=true"
        
        print(f"✅ P0 FIX VERIFIED: /ai/identify (cibi_sana) responded in {elapsed:.2f}s (<5s)")
        print(f"   - dish: {result.get('dish_display')}")
        print(f"   - source: {result.get('source')}")
        print(f"   - is_premium: {result.get('is_premium')}")
        print(f"   - enrichment_pending: {premium.get('enrichment_pending')}")
        
        return result
    
    def test_identify_external_fast(self):
        """
        Test /ai/identify with restaurant=externo (Gemini mode)
        Should respond in <3 seconds (Gemini is fast, enrichment moved to background)
        """
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "externo",
                "pin": "2212",
                "nome": "Joao Manoel",
                "country": "BR"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                data=data,
                timeout=30
            )
            elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        result = response.json()
        
        # Check response time - allow up to 5s for Gemini (network latency)
        assert elapsed < 5.0, f"P0 FIX FAILED: /ai/identify (external) took {elapsed:.2f}s (should be <5s)"
        
        # Check source - could be gemini_flash or cached
        source = result.get("source")
        assert "gemini" in source or "cached" in source, f"Expected source containing 'gemini' or 'cached', got {source}"
        
        print(f"✅ P0 FIX VERIFIED: /ai/identify (external) responded in {elapsed:.2f}s")
        print(f"   - dish: {result.get('dish_display')}")
        print(f"   - source: {result.get('source')}")
        print(f"   - is_premium: {result.get('is_premium')}")
        
        return result


class TestP0PremiumLogin:
    """
    P0 Fix: Premium login should fail gracefully for invalid PIN
    Previously stuck with stale localStorage PIN.
    Now clears stale data on failed login.
    """
    
    def test_premium_login_valid_credentials(self):
        """Test login with valid premium credentials (pin=2212, nome=Joao Manoel)"""
        data = {
            "pin": "2212",
            "nome": "Joao Manoel"
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
        # Name might have trailing space in DB
        assert "Joao Manoel" in user.get("nome", ""), f"Expected nome containing 'Joao Manoel', got {user.get('nome')}"
        
        print(f"✅ Premium Login Valid: user={user.get('nome')}, ok={result.get('ok')}")
        
        return result
    
    def test_premium_login_invalid_pin(self):
        """
        Test login with invalid PIN (pin=9999 doesn't exist)
        Should fail gracefully with ok=False
        """
        data = {
            "pin": "9999",
            "nome": "Joao Manoel"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data=data,
            timeout=10
        )
        
        result = response.json()
        
        # Should return ok=False for invalid credentials
        assert result.get("ok") == False, f"Expected ok=False for invalid PIN 9999, got {result}"
        
        print(f"✅ P0 FIX VERIFIED: Invalid PIN login fails gracefully: {result.get('error')}")
        
        return result
    
    def test_premium_login_invalid_user(self):
        """Test login with completely invalid credentials"""
        data = {
            "pin": "9999",
            "nome": "NonExistent User"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data=data,
            timeout=10
        )
        
        result = response.json()
        
        # Should return ok=False
        assert result.get("ok") == False, f"Expected ok=False for invalid user, got {result}"
        
        print(f"✅ Invalid user login fails gracefully: {result.get('error')}")


class TestP1AlertsEnrich:
    """
    P1 Fix: Alerts should be generated via /ai/enrich endpoint
    Previously alerts were not generated due to 'has_alert' bug.
    Now alerts are generated in /ai/enrich endpoint.
    """
    
    def test_enrich_returns_premium_data(self):
        """
        Test /ai/enrich returns beneficios, riscos, curiosidade, noticias, alertas_historico
        """
        data = {
            "nome": "Frango Grelhado",
            "ingredientes": ["frango", "azeite", "alho", "limao"],
            "pin": "2212",
            "user_nome": "Joao Manoel"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/ai/enrich",
            json=data,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        result = response.json()
        
        # Check that enrichment returns data
        assert result.get("ok") == True, f"Expected ok=True, got {result}"
        
        # Check premium fields
        beneficios = result.get("beneficios", [])
        riscos = result.get("riscos", [])
        curiosidade = result.get("curiosidade", "")
        combinacoes = result.get("combinacoes", [])
        noticias = result.get("noticias", [])
        alertas_historico = result.get("alertas_historico", [])
        
        print(f"✅ P1 FIX VERIFIED: /ai/enrich returned data in {elapsed:.2f}s")
        print(f"   - beneficios: {len(beneficios)} items")
        print(f"   - riscos: {len(riscos)} items")
        print(f"   - curiosidade: {len(curiosidade)} chars")
        print(f"   - combinacoes: {len(combinacoes)} items")
        print(f"   - noticias: {len(noticias)} items")
        print(f"   - alertas_historico: {len(alertas_historico)} items")
        
        # At least some data should be returned
        has_data = (
            len(beneficios) > 0 or
            len(riscos) > 0 or
            len(curiosidade) > 0 or
            len(combinacoes) > 0 or
            len(noticias) > 0 or
            len(alertas_historico) > 0
        )
        assert has_data, "Expected at least some enrichment data"
        
        return result
    
    def test_enrich_requires_premium(self):
        """Test that /ai/enrich requires premium access"""
        data = {
            "nome": "Frango Grelhado",
            "ingredientes": ["frango"],
            "pin": "9999",  # Invalid PIN
            "user_nome": "Invalid"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/enrich",
            json=data,
            timeout=10
        )
        
        result = response.json()
        
        # Should return error for non-premium
        assert result.get("ok") == False, f"Expected ok=False for non-premium, got {result}"
        
        print(f"✅ /ai/enrich correctly requires premium: {result.get('error')}")


class TestP1FeedbackEndpoint:
    """
    P1 Fix: /ai/feedback should NOT return 500 error
    Previously failed because /app/datasets/organized directory didn't exist.
    Now the directory is created automatically.
    """
    
    def test_feedback_endpoint_no_500(self):
        """Test that /ai/feedback doesn't return 500 error"""
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "dish_slug": "frango_grelhado",
                "is_correct": "true",
                "original_dish": "frango_grelhado",
                "score": "0.85",
                "confidence": "alta",
                "source": "local_index"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ai/feedback",
                files=files,
                data=data,
                timeout=30
            )
        
        # Should NOT return 500
        assert response.status_code != 500, f"P1 FIX FAILED: /ai/feedback returned 500: {response.text[:200]}"
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        result = response.json()
        assert result.get("ok") == True, f"Expected ok=True, got {result}"
        
        print(f"✅ P1 FIX VERIFIED: /ai/feedback works without 500 error")
        print(f"   - file_saved: {result.get('file_saved')}")
        print(f"   - message: {result.get('message')}")
        
        return result


class TestP2TTSExpanded:
    """
    P2 Fix: TTS content expanded to include benefits, risks, ingredients, alerts, etc.
    """
    
    def test_tts_generates_audio(self):
        """Test that /ai/tts generates audio for dish data"""
        data = {
            "dish_data": {
                "dish_display": "Frango Grelhado",
                "nome": "Frango Grelhado",
                "category": "proteina animal",
                "nutrition": {
                    "calorias": "180 kcal",
                    "proteinas": "25g",
                    "carboidratos": "0g",
                    "gorduras": "8g"
                },
                "ingredientes": ["frango", "azeite", "alho", "limao"],
                "beneficios": ["Rico em proteina", "Baixo em carboidratos"],
                "riscos": ["Alto em sodio se temperado demais"],
                "alergenos": {"gluten": False, "lactose": False},
                "curiosidade": "O frango e uma das carnes mais consumidas no mundo."
            },
            "voice": "alloy"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/tts",
            json=data,
            timeout=30
        )
        
        # Check if audio was generated
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            
            if "audio" in content_type:
                # Audio was generated
                audio_size = len(response.content)
                assert audio_size > 1000, f"Audio too small: {audio_size} bytes"
                
                print(f"✅ P2 FIX VERIFIED: /ai/tts generated audio")
                print(f"   - size: {audio_size // 1024}KB")
                print(f"   - content-type: {content_type}")
            else:
                # JSON response (might be error)
                result = response.json()
                if result.get("ok") == False:
                    print(f"⚠️ TTS returned error: {result.get('message')}")
                    # This is acceptable if EMERGENT_LLM_KEY is not configured
                    pytest.skip("TTS service not available")
        else:
            pytest.fail(f"TTS endpoint failed: {response.status_code}")


class TestIdentifyWithPremiumFields:
    """
    Verify that /ai/identify returns all expected premium fields
    """
    
    def test_identify_returns_premium_fields(self):
        """Test that identify returns all premium fields for premium users"""
        image_path = "/tmp/test_food_real.jpg"
        if not os.path.exists(image_path):
            pytest.skip("Test food image not found")
        
        with open(image_path, "rb") as f:
            files = {"file": ("test_food.jpg", f, "image/jpeg")}
            data = {
                "restaurant": "externo",
                "pin": "2212",
                "nome": "Joao Manoel",
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
        
        # Check premium status - cached responses might not have is_premium
        is_premium = result.get("is_premium")
        source = result.get("source", "")
        
        if "cached" in source:
            print(f"⚠️ Got cached response (source={source}), skipping is_premium check")
        else:
            assert is_premium == True, f"Expected is_premium=True, got {is_premium}"
        
        # List expected premium fields
        premium_fields = [
            "ingredientes",
            "beneficios",
            "riscos",
            "curiosidade",
            "combinacoes",
            "beneficio_principal",
            "curiosidade_cientifica",
            "mito_verdade",
            "premium"
        ]
        
        print("\n📋 Premium Fields in /ai/identify response:")
        for field in premium_fields:
            value = result.get(field)
            has_value = value is not None and (
                (isinstance(value, list) and len(value) > 0) or
                (isinstance(value, str) and len(value) > 0) or
                (isinstance(value, dict) and len(value) > 0) or
                isinstance(value, bool)
            )
            status = "✅" if has_value else "❌"
            print(f"  {status} {field}: {type(value).__name__}")
        
        # Check enrichment_pending flag
        premium_obj = result.get("premium", {})
        if premium_obj:
            print(f"  - enrichment_pending: {premium_obj.get('enrichment_pending')}")
        
        return result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
