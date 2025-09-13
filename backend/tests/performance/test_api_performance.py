"""
T113: API response time validation (<200ms requirement).

This module tests API performance to ensure all endpoints respond within 
the required 200ms threshold for a responsive user experience.

Following TDD methodology:
1. RED: Create failing tests for performance requirements  
2. GREEN: Optimize API performance to meet requirements
3. REFACTOR: Fine-tune and monitor performance

These tests MUST FAIL initially if performance requirements are not met.
"""
import pytest
import asyncio
import httpx
import time
from typing import Dict, Any, List
from datetime import datetime
import statistics

# Test configuration
BACKEND_BASE_URL = "http://localhost:8000"
PERFORMANCE_THRESHOLD_MS = 200  # Maximum acceptable response time in milliseconds
TEST_TIMEOUT = 30.0


class TestAPIResponseTimeValidation:
    """Performance tests for API response time validation."""
    
    @pytest.fixture(scope="class")
    async def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Login to get access token
            login_response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "TestP@ss_w0rd!"
            })
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            
            token_data = login_response.json()
            return {"Authorization": f"Bearer {token_data['access_token']}"}

    async def measure_response_time(self, client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Measure response time for an API call."""
        start_time = time.perf_counter()
        
        if method.upper() == "GET":
            response = await client.get(url, **kwargs)
        elif method.upper() == "POST":
            response = await client.post(url, **kwargs)
        elif method.upper() == "PUT":
            response = await client.put(url, **kwargs)
        elif method.upper() == "DELETE":
            response = await client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        end_time = time.perf_counter()
        response_time_ms = (end_time - start_time) * 1000
        
        return {
            "response": response,
            "response_time_ms": response_time_ms,
            "status_code": response.status_code
        }

    async def measure_multiple_calls(self, client: httpx.AsyncClient, method: str, url: str, iterations: int = 5, **kwargs) -> Dict[str, Any]:
        """Measure response time across multiple calls for statistical analysis."""
        response_times = []
        status_codes = []
        
        for _ in range(iterations):
            result = await self.measure_response_time(client, method, url, **kwargs)
            response_times.append(result["response_time_ms"])
            status_codes.append(result["status_code"])
            
            # Small delay between requests to avoid overwhelming the server
            await asyncio.sleep(0.1)
        
        return {
            "response_times": response_times,
            "average_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
            "status_codes": status_codes
        }

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_auth_endpoint_performance(self):
        """
        Test authentication endpoint performance.
        
        Requirements:
        - Login endpoint must respond within 200ms
        - Performance should be consistent across multiple calls
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test login performance
            login_data = {
                "email": "test@example.com",
                "password": "TestP@ss_w0rd!"
            }
            
            # Single call measurement
            result = await self.measure_response_time(client, "POST", "/api/v1/auth/login", json=login_data)
            
            assert result["status_code"] == 200, f"Login failed with status {result['status_code']}"
            assert result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Login endpoint took {result['response_time_ms']:.2f}ms, exceeds {PERFORMANCE_THRESHOLD_MS}ms threshold"
            
            # Multiple calls for consistency
            multi_result = await self.measure_multiple_calls(client, "POST", "/api/v1/auth/login", 5, json=login_data)
            
            assert multi_result["average_response_time"] < PERFORMANCE_THRESHOLD_MS, \
                f"Average login response time {multi_result['average_response_time']:.2f}ms exceeds threshold"
            assert multi_result["max_response_time"] < PERFORMANCE_THRESHOLD_MS * 1.5, \
                f"Max login response time {multi_result['max_response_time']:.2f}ms significantly exceeds threshold"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_content_listing_performance(self):
        """
        Test content listing endpoints performance.
        
        Requirements:
        - All listing endpoints must respond within 200ms
        - Performance should remain consistent with pagination
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test blog posts listing
            posts_result = await self.measure_response_time(client, "GET", "/api/v1/posts")
            assert posts_result["status_code"] == 200
            assert posts_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Posts listing took {posts_result['response_time_ms']:.2f}ms, exceeds threshold"
            
            # Test projects listing
            projects_result = await self.measure_response_time(client, "GET", "/api/v1/projects")
            assert projects_result["status_code"] == 200
            assert projects_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Projects listing took {projects_result['response_time_ms']:.2f}ms, exceeds threshold"
            
            # Test tags listing
            tags_result = await self.measure_response_time(client, "GET", "/api/v1/tags")
            assert tags_result["status_code"] == 200
            assert tags_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Tags listing took {tags_result['response_time_ms']:.2f}ms, exceeds threshold"
            
            # Test pagination performance
            paginated_result = await self.measure_response_time(client, "GET", "/api/v1/posts?page=1&limit=5")
            assert paginated_result["status_code"] == 200
            assert paginated_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Paginated posts took {paginated_result['response_time_ms']:.2f}ms, exceeds threshold"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """
        Test health check endpoint performance.
        
        Requirements:
        - Health check must be extremely fast (< 50ms)
        - Should be optimized for monitoring systems
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Health check should be very fast
            health_result = await self.measure_response_time(client, "GET", "/health")
            
            assert health_result["status_code"] == 200
            # Health check has stricter performance requirement
            assert health_result["response_time_ms"] < 50, \
                f"Health check took {health_result['response_time_ms']:.2f}ms, should be < 50ms"
            
            # Test consistency across multiple health checks
            multi_health = await self.measure_multiple_calls(client, "GET", "/health", 10)
            
            assert multi_health["average_response_time"] < 30, \
                f"Average health check time {multi_health['average_response_time']:.2f}ms should be < 30ms"
            assert multi_health["max_response_time"] < 50, \
                f"Max health check time {multi_health['max_response_time']:.2f}ms should be < 50ms"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_authenticated_endpoint_performance(self, auth_headers):
        """
        Test performance of authenticated endpoints.
        
        Requirements:
        - Protected endpoints must respond within 200ms including auth overhead
        - User profile retrieval should be fast for good UX
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test user profile retrieval
            profile_result = await self.measure_response_time(client, "GET", "/api/v1/users/me", headers=auth_headers)
            
            assert profile_result["status_code"] == 200
            assert profile_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"User profile retrieval took {profile_result['response_time_ms']:.2f}ms, exceeds threshold"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_content_creation_performance(self, auth_headers):
        """
        Test content creation performance.
        
        Requirements:
        - Content creation should respond within 200ms for good UX
        - Tag auto-creation should not significantly impact performance
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test blog post creation performance
            blog_data = {
                "title": f"Performance Test Blog Post {int(time.time())}",
                "content": "Testing blog creation performance with automatic tag generation.",
                "excerpt": "Performance test excerpt",
                "status": "published",
                "tag_names": ["Performance", "Testing", "API"]
            }
            
            blog_result = await self.measure_response_time(client, "POST", "/api/v1/posts", json=blog_data, headers=auth_headers)
            
            assert blog_result["status_code"] == 201
            assert blog_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Blog creation took {blog_result['response_time_ms']:.2f}ms, exceeds threshold"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_intensive_operations_performance(self):
        """
        Test performance of database-intensive operations.
        
        Requirements:
        - Complex queries with joins should still meet performance requirements
        """
        async with httpx.AsyncClient(base_url=BACKEND_BASE_URL, timeout=TEST_TIMEOUT) as client:
            # Test complex listing with relationships (posts with author and tags)
            complex_posts_result = await self.measure_response_time(client, "GET", "/api/v1/posts?limit=10")
            
            assert complex_posts_result["status_code"] == 200
            assert complex_posts_result["response_time_ms"] < PERFORMANCE_THRESHOLD_MS, \
                f"Complex posts query took {complex_posts_result['response_time_ms']:.2f}ms, exceeds threshold"