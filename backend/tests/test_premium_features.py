"""
SoulNutri Premium Features Tests
Tests for Premium profile, Radar info, and new features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PIN = "1234"
TEST_NOME = "Teste"


class TestRadarEndpoints:
    """Test Radar de Notícias endpoints - Salmão cativeiro and Ferro Heme"""
    
    def test_radar_salmao_cativeiro_info(self):
        """Test /api/radar/alimentos/salmao returns cativeiro warning"""
        response = requests.get(f"{BASE_URL}/api/radar/alimentos/salmao")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("ok") == True
        assert "radar" in data
        
        radar = data["radar"]
        assert radar.get("has_alert") == True
        
        # Check for cativeiro info
        message = radar.get("message", "").lower()
        titulo = radar.get("titulo", "").lower()
        voce_sabia = radar.get("voce_sabia", "").lower()
        
        has_cativeiro = "cativeiro" in message or "cativeiro" in titulo or "cativeiro" in voce_sabia
        assert has_cativeiro, "Salmão radar should mention 'cativeiro'"
        
        # Check for combinações
        assert "combinacoes" in radar
        assert len(radar["combinacoes"]) > 0
        
        # Check for voce_sabia
        assert "voce_sabia" in radar
        assert len(radar["voce_sabia"]) > 0
        
        print(f"✓ Salmão radar: cativeiro info present")
        print(f"  - Título: {radar.get('titulo')}")
        print(f"  - Combinações: {len(radar.get('combinacoes', []))} items")
    
    def test_radar_carne_bovina_ferro_heme(self):
        """Test /api/radar/alimentos/carne%20bovina returns Ferro Heme explanation"""
        response = requests.get(f"{BASE_URL}/api/radar/alimentos/carne%20bovina")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("ok") == True
        assert "radar" in data
        
        radar = data["radar"]
        assert radar.get("has_alert") == True
        
        # Check for ferro heme info in fatos_detalhados
        fatos = data.get("fatos_detalhados", [])
        assert len(fatos) > 0
        
        # Look for ferro heme explanation
        ferro_heme_found = False
        for fato in fatos:
            for f in fato.get("fatos", []):
                if "ferro heme" in f.get("titulo", "").lower() or "ferro heme" in f.get("resumo", "").lower():
                    ferro_heme_found = True
                    print(f"✓ Ferro Heme explanation found: {f.get('titulo')}")
                    break
        
        assert ferro_heme_found, "Carne bovina radar should explain Ferro Heme"
        
        # Check for combinações
        assert "combinacoes" in radar
        print(f"✓ Carne bovina radar: Ferro Heme info present")
    
    def test_radar_returns_voce_sabia(self):
        """Test that radar returns 'voce_sabia' field"""
        response = requests.get(f"{BASE_URL}/api/radar/alimentos/ovo")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("ok"):
            radar = data.get("radar", {})
            if radar.get("has_alert"):
                assert "voce_sabia" in radar
                print(f"✓ Radar returns voce_sabia: {radar.get('voce_sabia', '')[:50]}...")
    
    def test_radar_returns_combinacoes(self):
        """Test that radar returns 'combinacoes' field"""
        response = requests.get(f"{BASE_URL}/api/radar/alimentos/feijao")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("ok"):
            radar = data.get("radar", {})
            if radar.get("has_alert"):
                assert "combinacoes" in radar
                assert isinstance(radar["combinacoes"], list)
                print(f"✓ Radar returns combinacoes: {len(radar.get('combinacoes', []))} items")


class TestPremiumProfileEndpoints:
    """Test Premium profile get and update endpoints"""
    
    def test_get_profile_endpoint_exists(self):
        """Test /api/premium/get-profile endpoint exists"""
        response = requests.get(
            f"{BASE_URL}/api/premium/get-profile",
            params={"pin": TEST_PIN, "nome": TEST_NOME}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return ok=True if user exists, ok=False if not
        assert "ok" in data
        
        if data.get("ok"):
            assert "profile" in data
            profile = data["profile"]
            # Check profile structure
            assert "nome" in profile
            assert "peso" in profile
            assert "altura" in profile
            assert "idade" in profile
            assert "sexo" in profile
            assert "nivel_atividade" in profile
            assert "objetivo" in profile
            assert "restricoes" in profile
            print(f"✓ Get profile: {profile.get('nome')} - {profile.get('peso')}kg")
        else:
            print(f"✓ Get profile endpoint works (user not found: {data.get('error')})")
    
    def test_update_profile_endpoint_exists(self):
        """Test /api/premium/update-profile endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/premium/update-profile",
            data={
                "pin": TEST_PIN,
                "nome": TEST_NOME,
                "peso": 70,
                "altura": 175,
                "idade": 30,
                "sexo": "M",
                "nivel_atividade": "moderado",
                "objetivo": "manter",
                "restricoes": ""
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return ok=True if user exists, ok=False if not
        assert "ok" in data
        
        if data.get("ok"):
            assert "meta_calorica" in data
            assert "message" in data
            print(f"✓ Update profile: {data.get('message')}")
        else:
            print(f"✓ Update profile endpoint works (user not found: {data.get('error')})")
    
    def test_update_profile_recalculates_meta(self):
        """Test that updating profile recalculates caloric meta"""
        # First get current profile
        get_response = requests.get(
            f"{BASE_URL}/api/premium/get-profile",
            params={"pin": TEST_PIN, "nome": TEST_NOME}
        )
        
        if get_response.status_code == 200 and get_response.json().get("ok"):
            # Update with different weight
            update_response = requests.post(
                f"{BASE_URL}/api/premium/update-profile",
                data={
                    "pin": TEST_PIN,
                    "nome": TEST_NOME,
                    "peso": 80,  # Different weight
                    "altura": 175,
                    "idade": 30,
                    "sexo": "M",
                    "nivel_atividade": "intenso",  # Different activity
                    "objetivo": "ganhar",  # Different goal
                    "restricoes": "sem_gluten"
                }
            )
            
            assert update_response.status_code == 200
            data = update_response.json()
            
            if data.get("ok"):
                meta = data.get("meta_calorica", {})
                assert "meta_sugerida" in meta
                assert "objetivo" in meta
                assert meta["objetivo"] == "ganhar"
                print(f"✓ Meta recalculated: {meta.get('meta_sugerida')} kcal for 'ganhar' goal")


class TestPremiumLogin:
    """Test Premium login endpoint"""
    
    def test_login_endpoint(self):
        """Test /api/premium/login endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data={"nome": TEST_NOME, "pin": TEST_PIN}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "ok" in data
        if data.get("ok"):
            assert "user" in data
            print(f"✓ Login successful: {data.get('user', {}).get('nome')}")
        else:
            print(f"✓ Login endpoint works (error: {data.get('error')})")


class TestDishIdentification:
    """Test dish identification with radar info"""
    
    def test_identify_returns_dish_info(self):
        """Test /api/ai/identify returns complete dish info"""
        test_image = "/app/datasets/organized/aboboraaocurry/aboboraaocurry.jpeg"
        if not os.path.exists(test_image):
            pytest.skip(f"Test image not found: {test_image}")
        
        with open(test_image, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/ai/identify", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert data.get("identified") == True
        
        # Check for required fields
        assert "dish_display" in data
        assert "ingredientes" in data
        assert "beneficios" in data
        
        print(f"✓ Identified: {data.get('dish_display')}")
        print(f"  - Ingredientes: {len(data.get('ingredientes', []))} items")
        print(f"  - Benefícios: {len(data.get('beneficios', []))} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
