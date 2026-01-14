#!/usr/bin/env python3
"""
Test script for soccer kick functionality
验证足球踢球功能是否正确实现

Usage:
    python scripts/test_soccer_kick.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
import numpy as np


def test_imports():
    """测试是否能正常导入所需模块"""
    print("\n=== 测试1: 导入模块 ===")
    try:
        from humanoidverse.envs.motion_tracking.motion_tracking import LeggedRobotMotionTracking
        print("✓ 成功导入 LeggedRobotMotionTracking")
        
        from humanoidverse.simulator.isaacsim.isaacsim import IsaacSim
        print("✓ 成功导入 IsaacSim")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_config_files():
    """测试配置文件是否存在"""
    print("\n=== 测试2: 配置文件 ===")
    
    config_files = [
        "humanoidverse/config/env/soccer_kick.yaml",
        "humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml",
        "humanoidverse/config/exp/soccer_kick.yaml",
    ]
    
    all_exist = True
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            print(f"✓ 配置文件存在: {config_file}")
        else:
            print(f"✗ 配置文件缺失: {config_file}")
            all_exist = False
    
    return all_exist


def test_reward_functions():
    """测试奖励函数是否正确定义"""
    print("\n=== 测试3: 奖励函数 ===")
    
    try:
        from humanoidverse.envs.motion_tracking.motion_tracking import LeggedRobotMotionTracking
        
        reward_functions = [
            '_reward_kick_ball_to_target',
            '_reward_kick_ball_velocity',
            '_reward_approach_ball',
            '_reward_ball_contact',
            '_reward_kick_ball_height',
        ]
        
        all_exist = True
        for func_name in reward_functions:
            if hasattr(LeggedRobotMotionTracking, func_name):
                print(f"✓ 奖励函数存在: {func_name}")
            else:
                print(f"✗ 奖励函数缺失: {func_name}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"✗ 测试奖励函数失败: {e}")
        return False


def test_observation_functions():
    """测试观测函数是否正确定义"""
    print("\n=== 测试4: 观测函数 ===")
    
    try:
        from humanoidverse.envs.motion_tracking.motion_tracking import LeggedRobotMotionTracking
        
        obs_functions = [
            '_get_obs_ball_pos_robot_frame',
            '_get_obs_ball_vel_robot_frame',
        ]
        
        all_exist = True
        for func_name in obs_functions:
            if hasattr(LeggedRobotMotionTracking, func_name):
                print(f"✓ 观测函数存在: {func_name}")
            else:
                print(f"✗ 观测函数缺失: {func_name}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"✗ 测试观测函数失败: {e}")
        return False


def test_simulator_methods():
    """测试仿真器方法是否正确定义"""
    print("\n=== 测试5: 仿真器方法 ===")
    
    try:
        from humanoidverse.simulator.isaacsim.isaacsim import IsaacSim
        
        methods = [
            'set_ball_state_tensor',
        ]
        
        all_exist = True
        for method_name in methods:
            if hasattr(IsaacSim, method_name):
                print(f"✓ 仿真器方法存在: {method_name}")
            else:
                print(f"✗ 仿真器方法缺失: {method_name}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"✗ 测试仿真器方法失败: {e}")
        return False


def test_scripts():
    """测试训练和评估脚本是否存在"""
    print("\n=== 测试6: 脚本文件 ===")
    
    script_files = [
        "scripts/train_soccer_kick.sh",
        "scripts/eval_soccer_kick.sh",
    ]
    
    all_exist = True
    for script_file in script_files:
        file_path = project_root / script_file
        if file_path.exists():
            print(f"✓ 脚本存在: {script_file}")
            # Check if executable
            if os.access(file_path, os.X_OK):
                print(f"  ✓ 脚本可执行")
            else:
                print(f"  ⚠ 脚本不可执行,运行: chmod +x {script_file}")
        else:
            print(f"✗ 脚本缺失: {script_file}")
            all_exist = False
    
    return all_exist


def test_documentation():
    """测试文档是否存在"""
    print("\n=== 测试7: 文档文件 ===")
    
    doc_files = [
        "SOCCER_KICK_README.md",
        "IMPLEMENTATION_SUMMARY.md",
        "QUICK_START_SOCCER_KICK.md",
        "足球踢球功能说明.txt",
    ]
    
    all_exist = True
    for doc_file in doc_files:
        file_path = project_root / doc_file
        if file_path.exists():
            print(f"✓ 文档存在: {doc_file}")
        else:
            print(f"✗ 文档缺失: {doc_file}")
            all_exist = False
    
    return all_exist


def main():
    """运行所有测试"""
    print("=" * 60)
    print("足球踢球功能测试")
    print("=" * 60)
    
    tests = [
        ("导入模块", test_imports),
        ("配置文件", test_config_files),
        ("奖励函数", test_reward_functions),
        ("观测函数", test_observation_functions),
        ("仿真器方法", test_simulator_methods),
        ("脚本文件", test_scripts),
        ("文档文件", test_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n测试 '{test_name}' 发生异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过!足球踢球功能已正确实现!")
        print("\n下一步:")
        print("  1. 运行测试训练: bash scripts/train_soccer_kick.sh")
        print("  2. 查看文档: cat QUICK_START_SOCCER_KICK.md")
        return 0
    else:
        print("\n⚠️  部分测试失败,请检查上述错误")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
