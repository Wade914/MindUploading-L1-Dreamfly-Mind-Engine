#!/usr/bin/env python3
"""
DreamFly API 综合测试脚本
测试所有主要API功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_basic_health():
    """测试基础健康检查"""
    print("=== 测试基础健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_interaction_apis():
    """测试交互记录相关API"""
    print("\n=== 测试交互记录相关API ===")
    
    try:
        # 测试记录交互
        print("\n1. 测试记录交互")
        interaction_data = {
            "user_id": "test_user_interaction",
            "mind_name": "Steve Jobs",
            "user_message": "请告诉我关于创新的看法",
            "ai_response": "创新不仅仅是技术的突破，更是对用户需求的深刻理解。",
            "tokens_used": 45
        }
        
        response = requests.post(f"{BASE_URL}/api/interaction/record", json=interaction_data, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 记录交互成功: {result['message']}")
            if 'data' in result and 'id' in result['data']:
                print(f"交互ID: {result['data']['id']}")
            
            # 测试获取交互统计
            print("\n2. 测试获取交互统计")
            stats_response = requests.get(
                f"{BASE_URL}/api/interaction/stats",
                params={
                    "user_id": interaction_data["user_id"],
                    "mind_name": interaction_data["mind_name"]
                },
                timeout=10
            )
            print(f"状态码: {stats_response.status_code}")
            if stats_response.status_code == 200:
                stats_result = stats_response.json()
                print(f"✅ 获取交互统计成功:")
                print(f"  总交互次数: {stats_result['data']['total_interactions']}")
                print(f"  总Token使用: {stats_result['data']['total_tokens']}")
            else:
                print(f"❌ 获取交互统计失败: {stats_response.text}")
        else:
            print(f"❌ 记录交互失败: {response.text}")
    except Exception as e:
        print(f"❌ 交互API测试失败: {e}")

def test_ttfd_apis():
    """测试TTFD测试结果相关API"""
    print("\n=== 测试TTFD测试结果相关API ===")

    try:
        # 测试保存TTFD测试结果
        print("\n1. 测试保存TTFD测试结果")
        ttfd_data = {
            "test_type": "ttfd",
            "results": {
                "score": 85,
                "questions_answered": 10,
                "user_responses": [
                    "我喜欢蓝色，因为它让我感到平静",
                    "我相信外星人存在，宇宙如此广阔",
                    "我认为命运掌握在自己手中"
                ],
                "consciousness_levels": [
                    {"name": "感知层", "value": 85},
                    {"name": "认知层", "value": 78},
                    {"name": "情感层", "value": 92}
                ],
                "completion_time": "2025-09-18T18:30:00Z"
            },
            "score": 85,
            "answers": {
                "responses": [
                    {
                        "question_index": 0,
                        "question": "你喜欢什么颜色？",
                        "answer": "我喜欢蓝色，因为它让我感到平静",
                        "timestamp": "18:25:30"
                    }
                ]
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/user/test-results?user_id=test_user_ttfd",
            json=ttfd_data,
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ TTFD测试结果保存成功: {result['message']}")
            test_result_id = result['data']['test_result']['id']

            # 测试获取TTFD测试结果
            print("\n2. 测试获取TTFD测试结果")
            get_response = requests.get(
                f"{BASE_URL}/api/user/test-results?user_id=test_user_ttfd&test_type=ttfd",
                timeout=10
            )
            print(f"状态码: {get_response.status_code}")
            if get_response.status_code == 200:
                get_result = get_response.json()
                ttfd_results = get_result['data']['test_results']
                print(f"✅ 获取TTFD测试结果成功，共 {len(ttfd_results)} 个结果")

                if ttfd_results:
                    latest_result = ttfd_results[0]
                    print(f"  最新TTFD得分: {latest_result['score']}")
                    print(f"  测试类型: {latest_result['test_type']}")
            else:
                print(f"❌ 获取TTFD测试结果失败: {get_response.text}")
        else:
            print(f"❌ 保存TTFD测试结果失败: {response.text}")
    except Exception as e:
        print(f"❌ TTFD API测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 DreamFly API 综合测试开始")
    print("=" * 50)

    # 基础健康检查
    if not test_basic_health():
        print("❌ 后端服务未启动，测试终止")
        return

    # 测试各个模块
    test_interaction_apis()
    test_ttfd_apis()

    print("\n" + "=" * 50)
    print("🎉 DreamFly API 综合测试完成")

if __name__ == "__main__":
    main()
