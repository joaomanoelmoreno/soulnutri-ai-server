# -*- coding: utf-8 -*-
"""
SoulNutri API Tests
Tests for the refactored backend that uses MongoDB dish_storage + S3 instead of local disk.
"""
import pytest
import requests
import os
from pathlib import Path

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL not set")

# Test image path
TEST_IMAGE_PATH = Path("/app/datasets/organized/Abobrinha Grelhada/20260125_112305.jpg")


class TestHealthEndpoints:
    """Health check endpoints"""
    
    def test_api_health(self):
        """GET /api/health - API health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ /api/health: {data}")


class TestAIStatus:
    """AI Index status endpoint - should return ready=true with 189 dishes"""
    
    def test_ai_status_ready(self):
        """GET /api/ai/status - deve retornar ready=true com 189 dishes"""
        response = requests.get(f"{BASE_URL}/api/ai/status", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data.get("ok") == True
        assert data.get("ready") == True
        assert "total_dishes" in data
        assert "total_embeddings" in data
        
        # Validate expected values
        total_dishes = data.get("total_dishes", 0)
        assert total_dishes >= 180, f"Expected ~189 dishes, got {total_dishes}"
        
        print(f"✅ /api/ai/status: ready={data['ready']}, dishes={total_dishes}, embeddings={data['total_embeddings']}")


class TestAIIdentify:
    """AI Identify endpoint - should identify dishes from images"""
    
    def test_identify_with_image(self):
        """POST /api/ai/identify - deve identificar o prato corretamente"""
        if not TEST_IMAGE_PATH.exists():
            pytest.skip(f"Test image not found: {TEST_IMAGE_PATH}")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/ai/identify",
                files=files,
                timeout=60
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data.get("ok") == True
        assert data.get("identified") == True
        assert "dish" in data or "dish_display" in data
        assert "confidence" in data
        assert "score" in data
        
        # Validate identification (should be Abobrinha Grelhada)
        dish_name = data.get("dish_display", data.get("dish", ""))
        assert "abobrinha" in dish_name.lower() or "grelhad" in dish_name.lower(), \
            f"Expected 'Abobrinha Grelhada', got '{dish_name}'"
        
        score = data.get("score", 0)
        assert score >= 0.5, f"Expected score >= 0.5, got {score}"
        
        print(f"✅ /api/ai/identify: dish={dish_name}, score={score:.2%}, confidence={data.get('confidence')}")


class TestAdminDishes:
    """Admin dishes endpoints - should return dishes from MongoDB"""
    
    def test_admin_dishes_list(self):
        """GET /api/admin/dishes - deve retornar lista de pratos com total ~217, sem duplicatas"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data.get("ok") == True
        assert "dishes" in data
        assert "total" in data
        
        dishes = data.get("dishes", [])
        total = data.get("total", 0)
        
        # Validate count
        assert total >= 180, f"Expected ~217 dishes, got {total}"
        assert len(dishes) == total, f"Dishes array length ({len(dishes)}) != total ({total})"
        
        # Check for duplicates using normalized slugs
        def norm(s): return s.lower().replace(' ', '_').replace('-', '_')
        seen_slugs = set()
        duplicates = []
        for dish in dishes:
            slug = dish.get("slug", "")
            n = norm(slug)
            if n in seen_slugs:
                duplicates.append(slug)
            seen_slugs.add(n)
        
        assert len(duplicates) == 0, f"Found duplicate slugs: {duplicates[:5]}"
        
        # Check that known dishes have image_count > 0
        dishes_with_images = [d for d in dishes if d.get("image_count", 0) > 0]
        assert len(dishes_with_images) > 100, f"Expected >100 dishes with images, got {len(dishes_with_images)}"
        
        print(f"✅ /api/admin/dishes: total={total}, with_images={len(dishes_with_images)}, no_duplicates=True")
    
    def test_admin_dishes_full(self):
        """GET /api/admin/dishes-full - deve retornar lista completa com all_images, first_image"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes-full", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data.get("ok") == True
        assert "dishes" in data
        
        dishes = data.get("dishes", [])
        assert len(dishes) > 0, "No dishes returned"
        
        # Check first dish has expected fields
        first_dish = dishes[0]
        expected_fields = ["slug", "nome", "categoria", "image_count", "all_images", "first_image"]
        for field in expected_fields:
            assert field in first_dish, f"Missing field: {field}"
        
        # Check that dishes with images have all_images populated
        dishes_with_images = [d for d in dishes if d.get("image_count", 0) > 0]
        for dish in dishes_with_images[:5]:  # Check first 5
            all_images = dish.get("all_images", [])
            first_image = dish.get("first_image")
            image_count = dish.get("image_count", 0)
            
            assert len(all_images) == image_count, \
                f"Dish {dish['slug']}: all_images length ({len(all_images)}) != image_count ({image_count})"
            
            if image_count > 0:
                assert first_image is not None, f"Dish {dish['slug']}: first_image is None but image_count={image_count}"
        
        print(f"✅ /api/admin/dishes-full: total={len(dishes)}, with_images={len(dishes_with_images)}")


class TestAdminDishImage:
    """Admin dish image endpoint - should return images from S3 with local fallback"""
    
    def test_dish_image_known_dish(self):
        """GET /api/admin/dish-image/{slug} - deve retornar imagem com HTTP 200"""
        # Test with a known dish (URL encoded)
        test_slugs = [
            "Abobora ao Curry",
            "Abobrinha Grelhada",
            "Arroz Integral com Legumes"
        ]
        
        success_count = 0
        for slug in test_slugs:
            response = requests.get(
                f"{BASE_URL}/api/admin/dish-image/{slug}",
                timeout=30
            )
            
            if response.status_code == 200:
                # Validate it's an image
                content_type = response.headers.get("content-type", "")
                assert "image" in content_type, f"Expected image content-type, got {content_type}"
                assert len(response.content) > 1000, f"Image too small: {len(response.content)} bytes"
                success_count += 1
                print(f"  ✅ {slug}: {len(response.content)} bytes")
            else:
                print(f"  ⚠️ {slug}: HTTP {response.status_code}")
        
        assert success_count >= 1, f"Expected at least 1 image to load, got {success_count}"
        print(f"✅ /api/admin/dish-image: {success_count}/{len(test_slugs)} images loaded")


class TestUploadStatus:
    """Upload status endpoint - should return stats from MongoDB dish_storage"""
    
    def test_upload_status(self):
        """GET /api/upload/status - deve retornar total_dishes e total_images do MongoDB"""
        response = requests.get(f"{BASE_URL}/api/upload/status", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data.get("ok") == True
        assert "total_dishes" in data
        assert "total_images" in data
        
        total_dishes = data.get("total_dishes", 0)
        total_images = data.get("total_images", 0)
        
        # Validate values
        assert total_dishes > 0, f"Expected total_dishes > 0, got {total_dishes}"
        assert total_images > 0, f"Expected total_images > 0, got {total_images}"
        
        print(f"✅ /api/upload/status: dishes={total_dishes}, images={total_images}")


class TestNoDuplicates:
    """Verify no duplicates in admin dishes list"""
    
    def test_no_duplicate_slugs(self):
        """Verificar que não há duplicatas na lista de pratos admin (slug normalizado)"""
        response = requests.get(f"{BASE_URL}/api/admin/dishes", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        dishes = data.get("dishes", [])
        
        # Normalize slugs for comparison
        def norm(s): return s.lower().replace(' ', '_').replace('-', '_').replace('__', '_')
        
        slug_to_dishes = {}
        for dish in dishes:
            slug = dish.get("slug", "")
            n = norm(slug)
            if n not in slug_to_dishes:
                slug_to_dishes[n] = []
            slug_to_dishes[n].append(slug)
        
        # Find duplicates
        duplicates = {k: v for k, v in slug_to_dishes.items() if len(v) > 1}
        
        if duplicates:
            print(f"⚠️ Found {len(duplicates)} duplicate normalized slugs:")
            for norm_slug, originals in list(duplicates.items())[:5]:
                print(f"  - {norm_slug}: {originals}")
        
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate slugs"
        print(f"✅ No duplicates: {len(dishes)} unique dishes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
