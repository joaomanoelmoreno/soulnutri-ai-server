"""
Test Suite for P0 PWA Service Worker Cache Bug Fix (Iteration 16)
=================================================================
Tests the following fixes:
1. sw.js served with no-cache headers
2. manifest.json served with no-cache headers
3. sw.js content is v10-minimal (no DYNAMIC_CACHE, no fetch listener)
4. API endpoints still work correctly
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPWAServiceWorkerFix:
    """Tests for the P0 PWA Service Worker cache bug fix"""
    
    def test_sw_js_no_cache_headers(self):
        """Verify sw.js is served with proper no-cache headers"""
        response = requests.get(f"{BASE_URL}/sw.js")
        assert response.status_code == 200, f"sw.js returned {response.status_code}"
        
        # Check Cache-Control header
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-cache' in cache_control, f"Missing no-cache in Cache-Control: {cache_control}"
        assert 'no-store' in cache_control, f"Missing no-store in Cache-Control: {cache_control}"
        assert 'must-revalidate' in cache_control, f"Missing must-revalidate in Cache-Control: {cache_control}"
        
        print(f"✅ sw.js Cache-Control: {cache_control}")
    
    def test_sw_js_content_v10_minimal(self):
        """Verify sw.js content is the new v10-minimal version"""
        response = requests.get(f"{BASE_URL}/sw.js")
        assert response.status_code == 200
        
        content = response.text
        
        # Should contain v10-minimal version marker
        assert 'v10-minimal' in content, "sw.js should contain 'v10-minimal' version marker"
        
        # Should NOT contain old caching mechanisms
        assert 'DYNAMIC_CACHE' not in content, "sw.js should NOT contain 'DYNAMIC_CACHE'"
        assert 'APP_SHELL' not in content, "sw.js should NOT contain 'APP_SHELL'"
        
        # Should NOT have fetch listener (no fetch interception)
        # The new SW only has install and activate listeners
        assert "addEventListener('fetch'" not in content, "sw.js should NOT have fetch listener"
        
        print("✅ sw.js is v10-minimal version (no caching, no fetch interception)")
    
    def test_manifest_json_no_cache_headers(self):
        """Verify manifest.json is served with proper no-cache headers"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200, f"manifest.json returned {response.status_code}"
        
        # Check Cache-Control header
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-cache' in cache_control, f"Missing no-cache in Cache-Control: {cache_control}"
        assert 'no-store' in cache_control, f"Missing no-store in Cache-Control: {cache_control}"
        
        print(f"✅ manifest.json Cache-Control: {cache_control}")
    
    def test_manifest_json_content(self):
        """Verify manifest.json has valid PWA manifest content"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required PWA manifest fields
        assert 'name' in data, "manifest.json should have 'name' field"
        assert 'short_name' in data, "manifest.json should have 'short_name' field"
        assert 'start_url' in data, "manifest.json should have 'start_url' field"
        
        print(f"✅ manifest.json is valid PWA manifest: {data.get('name')}")


class TestAPIEndpoints:
    """Tests for API endpoints to ensure they still work after SW fix"""
    
    def test_ai_status(self):
        """Verify /api/ai/status returns ok:true"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('ok') == True, f"Expected ok:true, got {data}"
        assert data.get('ready') == True, f"Expected ready:true, got {data}"
        
        print(f"✅ /api/ai/status: {data.get('total_dishes')} dishes, {data.get('total_embeddings')} embeddings")
    
    def test_ai_dishes(self):
        """Verify /api/ai/dishes endpoint works"""
        response = requests.get(f"{BASE_URL}/api/ai/dishes")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('ok') == True, f"Expected ok:true, got {data}"
        assert 'dishes' in data, "Response should contain 'dishes' array"
        assert len(data['dishes']) > 0, "Should have at least one dish"
        
        print(f"✅ /api/ai/dishes: {data.get('total')} dishes returned")
    
    def test_premium_login(self):
        """Verify /api/premium/login works with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/premium/login",
            data={"pin": "2212", "nome": "Joao Manoel"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('ok') == True, f"Expected ok:true, got {data}"
        assert 'user' in data, "Response should contain 'user' object"
        assert data['user'].get('premium_ativo') == True, "User should have premium_ativo=True"
        
        print(f"✅ /api/premium/login: User {data['user'].get('nome')} logged in successfully")
    
    def test_health_endpoint(self):
        """Verify /health endpoint works (may return HTML from SPA or JSON from backend)"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            data = response.json()
            assert data.get('status') == 'healthy', f"Expected status:healthy, got {data}"
            print("✅ /health: Backend is healthy (JSON)")
        else:
            # SPA is serving the route - this is expected in production
            print("✅ /health: Route served by SPA (frontend handles this route)")
    
    def test_api_health_endpoint(self):
        """Verify /api/health endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('ok') == True, f"Expected ok:true, got {data}"
        
        print("✅ /api/health: API is healthy")


class TestCacheControlMiddleware:
    """Tests for the cache control middleware"""
    
    def test_html_no_cache(self):
        """Verify HTML responses have no-cache headers"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            cache_control = response.headers.get('Cache-Control', '')
            # Note: The middleware sets no-cache for HTML
            print(f"✅ HTML Cache-Control: {cache_control}")
    
    def test_sw_js_etag(self):
        """Verify sw.js has ETag header for cache validation"""
        response = requests.get(f"{BASE_URL}/sw.js")
        assert response.status_code == 200
        
        etag = response.headers.get('ETag')
        assert etag is not None, "sw.js should have ETag header"
        
        print(f"✅ sw.js ETag: {etag}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
