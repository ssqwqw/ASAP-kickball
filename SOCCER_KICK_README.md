# 足球踢球训练功能说明

## 概述

本文档说明如何使用新添加的足球踢球训练功能,训练G1人形机器人进行足球射门动作。

## 新增功能

### 1. 环境中的足球实例

在IsaacSim仿真环境中添加了足球实例,具有以下特性:
- **球的物理属性**:
  - 半径: 11cm (标准足球)
  - 质量: 450g
  - 摩擦系数: 0.6
  - 弹性系数: 0.7

- **球的初始位置**: 
  - 在机器人前方0.8-1.2米
  - 左右偏移-0.2到0.2米(随机化)
  - 目标(球门)位置在机器人前方5米处

### 2. 踢球相关的奖励函数

添加了5个专门的踢球奖励函数:

1. **`kick_ball_to_target`** (权重: 5.0)
   - 奖励球向目标移动的距离
   - 只有在球被踢动后才给予奖励

2. **`kick_ball_velocity`** (权重: 3.0)
   - 奖励球的速度方向是否朝向目标
   - 考虑速度大小和方向对齐度

3. **`approach_ball`** (权重: 2.0)
   - 奖励机器人接近足球
   - 只在球未被踢动前给予

4. **`ball_contact`** (权重: 1.5)
   - 奖励脚与球的接触
   - 检测距离阈值为15cm

5. **`kick_ball_height`** (权重: -1.0)
   - 惩罚球飞得过高
   - 鼓励地面射门

### 3. 观测空间扩展

添加了球相关的观测:
- `_get_obs_ball_pos_robot_frame()`: 球在机器人坐标系中的位置
- `_get_obs_ball_vel_robot_frame()`: 球在机器人坐标系中的速度

### 4. 配置文件

创建了以下新配置文件:

- **环境配置**: `humanoidverse/config/env/soccer_kick.yaml`
  - 定义了足球相关的环境参数
  
- **奖励配置**: `humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml`
  - 定义了踢球任务的奖励权重和参数
  
- **实验配置**: `humanoidverse/config/exp/soccer_kick.yaml`
  - 整合所有配置用于训练

## 使用方法

### 训练命令

```bash
python humanoidverse/train_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=4096 \
    headless=True
```

### 评估命令

```bash
python humanoidverse/eval_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=1 \
    headless=False \
    checkpoint_path=<你的检查点路径>
```

## 参数调整建议

### 1. 调整球的初始位置

在 `humanoidverse/config/env/soccer_kick.yaml` 中修改:

```yaml
soccer_ball:
  ball_distance_range: [0.8, 1.2]  # 调整球距离机器人的范围
  ball_lateral_range: [-0.2, 0.2]   # 调整球的横向偏移
  target_distance: 5.0              # 调整目标距离
```

### 2. 调整奖励权重

在 `humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml` 中修改:

```yaml
reward_scales:
  kick_ball_to_target: 5.0      # 主要奖励
  kick_ball_velocity: 3.0       # 速度奖励
  approach_ball: 2.0            # 接近球奖励
  ball_contact: 1.5             # 接触奖励
  kick_ball_height: -1.0        # 高度惩罚
```

### 3. 训练阶段性调整建议

**阶段1 - 接近球 (前1000次迭代)**
- 增加 `approach_ball` 权重到 4.0
- 降低 `kick_ball_to_target` 到 2.0

**阶段2 - 接触球 (1000-3000次迭代)**
- 增加 `ball_contact` 权重到 3.0
- 保持其他权重不变

**阶段3 - 准确踢球 (3000次迭代后)**
- 使用默认权重配置
- 可以增加 `kick_ball_to_target` 到 8.0

## 代码修改说明

### 主要修改的文件

1. **`humanoidverse/simulator/isaacsim/isaacsim.py`**
   - 添加了 `RigidObject` 导入
   - 在 `_setup_scene()` 中添加足球实例
   - 在 `refresh_sim_tensors()` 中更新球的状态
   - 添加了 `set_ball_state_tensor()` 方法

2. **`humanoidverse/envs/motion_tracking/motion_tracking.py`**
   - 在 `_init_buffers()` 中添加球相关缓冲区
   - 添加 `_reset_ball_states()` 方法重置球的位置
   - 在 `_pre_compute_observations_callback()` 中计算球的观测
   - 添加5个踢球奖励函数
   - 添加观测获取函数

## 观测空间说明

如果需要在观测中使用球的信息,在观测配置文件中添加:

```yaml
obs:
  actor_obs:
    # 其他观测...
    ball_pos_robot_frame: True  # 球的位置(3维)
    ball_vel_robot_frame: True  # 球的速度(3维)
```

## 注意事项

1. **内存占用**: 每个环境都有一个独立的球实例,大规模并行时注意内存
2. **碰撞检测**: 确保球和机器人的碰撞检测正确配置
3. **初始动作**: 建议使用包含踢球动作的参考动作作为起点
4. **训练时间**: 踢球是复杂任务,可能需要较长训练时间(>10M steps)

## 调试建议

1. **可视化球的轨迹**: 在无头模式关闭时可以看到球的运动
2. **监控奖励**: 使用tensorboard监控各项奖励的变化
3. **检查球的状态**: 打印 `self.ball_pos_global` 和 `self.ball_vel_global`

## 下一步改进方向

1. 添加多个球的支持
2. 添加对手守门员
3. 实现更复杂的足球技能(盘带、传球等)
4. 添加课程学习策略
5. 集成视觉输入用于球的检测

## 联系与支持

如有问题,请查看代码中的注释或联系开发者。
