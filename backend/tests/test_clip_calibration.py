"""
Test CLIP Calibration Features
- GET /api/ai/calibration endpoint
- POST /api/ai/feedback with score/confidence/source
- Thresholds verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://soulnutri-audit.preview.emergentagent.com')


class TestCalibrationEndpoint:
    """Tests for GET /api/ai/calibration endpoint"""
    
    def test_calibration_returns_ok(self):
        """Test that calibration endpoint returns ok=true"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        print(f"✅ Calibration endpoint returns ok=true")
    
    def test_calibration_has_stats(self):
        """Test that calibration returns stats object"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert response.status_code == 200
        data = response.json()
        assert 'stats' in data
        stats = data['stats']
        assert 'total_samples' in stats
        assert 'correct_count' in stats
        assert 'incorrect_count' in stats
        print(f"✅ Calibration has stats: {stats['total_samples']} samples")
    
    def test_calibration_has_distribution(self):
        """Test that calibration returns distribution object"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert response.status_code == 200
        data = response.json()
        assert 'distribution' in data
        dist = data['distribution']
        # Check expected ranges
        expected_ranges = ['0.90_1.00', '0.85_0.90', '0.80_0.85', '0.75_0.80', 
                          '0.70_0.75', '0.65_0.70', '0.60_0.65', '0.50_0.60', '0.00_0.50']
        for r in expected_ranges:
            assert r in dist, f"Missing range {r}"
            assert 'correct' in dist[r]
            assert 'incorrect' in dist[r]
        print(f"✅ Calibration has distribution with {len(dist)} ranges")
    
    def test_calibration_has_current_thresholds(self):
        """Test that calibration returns current_thresholds"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert response.status_code == 200
        data = response.json()
        assert 'current_thresholds' in data
        thresholds = data['current_thresholds']
        assert 'alta' in thresholds
        assert 'media' in thresholds
        assert 'rejeicao' in thresholds
        # Verify threshold values
        assert thresholds['alta'] == 0.85, f"Expected alta=0.85, got {thresholds['alta']}"
        assert thresholds['media'] == 0.50, f"Expected media=0.50, got {thresholds['media']}"
        assert thresholds['rejeicao'] == 0.50, f"Expected rejeicao=0.50, got {thresholds['rejeicao']}"
        print(f"✅ Thresholds correct: alta={thresholds['alta']}, media={thresholds['media']}, rejeicao={thresholds['rejeicao']}")


class TestFeedbackEndpoint:
    """Tests for POST /api/ai/feedback with new fields"""
    
    def test_feedback_accepts_score_confidence_source(self):
        """Test that feedback endpoint accepts score, confidence, source params"""
        # Create a minimal test image (1x1 pixel JPEG)
        import io
        from PIL import Image
        
        img = Image.new('RGB', (10, 10), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        data = {
            'dish_slug': 'arrozbranco',
            'is_correct': 'true',
            'score': '0.87',
            'confidence': 'alta',
            'source': 'local_index'
        }
        
        response = requests.post(f"{BASE_URL}/api/ai/feedback", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert result.get('ok') == True
        print(f"✅ Feedback endpoint accepts score/confidence/source: {result.get('message')}")


class TestAIStatus:
    """Tests for AI status and thresholds"""
    
    def test_ai_status_ready(self):
        """Test that AI index is ready"""
        response = requests.get(f"{BASE_URL}/api/ai/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert data.get('ready') == True
        print(f"✅ AI Status: ready={data.get('ready')}, dishes={data.get('total_dishes')}")


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        print(f"✅ Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
