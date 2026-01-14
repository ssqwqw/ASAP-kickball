# 足球踢球功能实现总结

## 实现日期
2026年1月13日

## 任务目标
为G1人形机器人添加足球踢球训练功能,使其能够学习踢足球射门的动作。

## 完成的工作

### 1. 环境层面修改

#### 1.1 IsaacSim仿真器 (`humanoidverse/simulator/isaacsim/isaacsim.py`)

**修改内容:**
- 导入 `RigidObject` 和 `RigidObjectCfg` 类
- 在 `_setup_scene()` 方法中添加足球实例配置
  - 球半径: 0.11m (标准足球)
  - 球质量: 0.45kg
  - 摩擦系数: 0.6
  - 弹性系数: 0.7 (用于反弹)
  - 初始位置: 机器人前方1米,高度为球半径
- 在 `refresh_sim_tensors()` 方法中添加球状态更新
  - `ball_root_states`: 球的完整状态(位置、旋转、速度)
  - `ball_pos`: 球的位置
  - `ball_rot`: 球的旋转
  - `ball_lin_vel`: 球的线速度
  - `ball_ang_vel`: 球的角速度
- 添加 `set_ball_state_tensor()` 方法用于重置球的状态

**代码位置:**
- 第15行: 添加导入
- 第467-502行: 添加球的配置
- 第697-702行: 更新球的状态
- 第719-724行: 添加重置球状态的方法

#### 1.2 动作跟踪环境 (`humanoidverse/envs/motion_tracking/motion_tracking.py`)

**修改内容:**

**a) 缓冲区初始化 (_init_buffers)**
- 添加球相关的缓冲区:
  - `ball_init_pos`: 球的初始位置
  - `ball_target_pos`: 目标(球门)位置
  - `ball_initial_distance`: 球到目标的初始距离
  - `ball_kicked`: 标记球是否已被踢动

**b) 域随机化缓冲区 (_init_domain_rand_buffers)**
- 添加足球参数配置:
  - `ball_distance_range`: 球距机器人的范围 [0.8, 1.2]米
  - `ball_lateral_range`: 球的横向偏移 [-0.2, 0.2]米
  - `target_distance`: 目标距离 5.0米
  - `kick_velocity_threshold`: 踢球速度阈值 2.0 m/s

**c) 重置回调 (_reset_tasks_callback)**
- 添加球状态重置调用 `_reset_ball_states()`

**d) 球状态重置 (_reset_ball_states)**
- 随机化球的初始位置(在机器人前方)
- 设置目标位置
- 计算初始距离
- 重置踢球标志
- 调用仿真器设置球的状态

**e) 观测计算 (_pre_compute_observations_callback)**
- 计算球在机器人坐标系中的位置和速度
- 计算球到目标的距离
- 检测球是否被踢动(速度超过阈值)

**f) 观测获取函数**
- `_get_obs_ball_pos_robot_frame()`: 获取球在机器人坐标系中的位置
- `_get_obs_ball_vel_robot_frame()`: 获取球在机器人坐标系中的速度

**g) 奖励函数 (5个新函数)**

1. **`_reward_kick_ball_to_target()`**
   - 目的: 奖励球向目标移动
   - 计算方法: 距离减少量 / 初始距离
   - 条件: 只有球被踢动后才给奖励

2. **`_reward_kick_ball_velocity()`**
   - 目的: 奖励球的速度方向正确
   - 计算方法: 速度大小 × 方向对齐度(余弦相似度)
   - 归一化到 [0, 1]

3. **`_reward_approach_ball()`**
   - 目的: 鼓励机器人接近球
   - 计算方法: exp(-最近脚到球距离 / 0.3)
   - 条件: 只在球未被踢动前给奖励

4. **`_reward_ball_contact()`**
   - 目的: 奖励与球接触
   - 计算方法: 二值奖励(距离 < 15cm)
   - 基于脚与球的距离

5. **`_reward_kick_ball_height()`**
   - 目的: 惩罚球飞得太高
   - 计算方法: -超过50cm的高度差
   - 条件: 只在球被踢动后惩罚

**代码位置:**
- 第154-160行: 添加球相关缓冲区
- 第162-175行: 初始化球参数
- 第168行: 添加重置球状态调用
- 第193-234行: 球状态重置方法
- 第348-368行: 球观测计算
- 第557-572行: 观测获取函数
- 第641-739行: 5个踢球奖励函数

### 2. 配置文件

#### 2.1 环境配置 (`humanoidverse/config/env/soccer_kick.yaml`)

**内容:**
- 继承自 `motion_tracking.yaml`
- 添加 `soccer_ball` 配置节:
  - 球的初始位置参数
  - 目标位置参数
  - 球的物理参数
  - 踢球检测阈值
- 调整终止条件(允许机器人蹲下准备踢球)
- 设置任务名称为 `soccer_kick`

#### 2.2 奖励配置 (`humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml`)

**内容:**
- 定义所有奖励权重:
  - 踢球奖励(主要): 5.0 - 10.0
  - 动作跟踪奖励(辅助): 0.3 - 1.0
  - 惩罚项: -0.3 到 -10.0
- 调整sigma参数以适应踢球任务
- 保留课程学习和限制设置

#### 2.3 实验配置 (`humanoidverse/config/exp/soccer_kick.yaml`)

**内容:**
- 指定使用PPO算法
- 指定使用soccer_kick环境
- 指定使用soccer_kick奖励配置
- 设置实验名称

### 3. 辅助工具

#### 3.1 训练脚本 (`scripts/train_soccer_kick.sh`)
- 自动化训练流程
- 设置默认参数
- 添加时间戳到实验名称

#### 3.2 评估脚本 (`scripts/eval_soccer_kick.sh`)
- 自动化评估流程
- 接收检查点路径作为参数
- 使用单环境和可视化模式

#### 3.3 可视化工具 (`scripts/vis/visualize_ball_trajectory.py`)
- 绘制球的轨迹(俯视图)
- 绘制球的高度随时间变化
- 绘制球的速度随时间变化
- 保存图像到文件

### 4. 文档

#### 4.1 使用说明 (`SOCCER_KICK_README.md`)
- 完整的功能说明
- 使用方法和命令示例
- 参数调整建议
- 训练阶段建议
- 调试建议
- 未来改进方向

#### 4.2 实现总结 (`IMPLEMENTATION_SUMMARY.md`)
- 本文档
- 详细的修改记录
- 代码位置说明

## 文件清单

### 修改的文件
1. `humanoidverse/simulator/isaacsim/isaacsim.py` - 添加足球实例
2. `humanoidverse/envs/motion_tracking/motion_tracking.py` - 添加踢球逻辑和奖励

### 新增的文件
1. `humanoidverse/config/env/soccer_kick.yaml` - 环境配置
2. `humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml` - 奖励配置
3. `humanoidverse/config/exp/soccer_kick.yaml` - 实验配置
4. `scripts/train_soccer_kick.sh` - 训练脚本
5. `scripts/eval_soccer_kick.sh` - 评估脚本
6. `scripts/vis/visualize_ball_trajectory.py` - 可视化工具
7. `SOCCER_KICK_README.md` - 使用文档
8. `IMPLEMENTATION_SUMMARY.md` - 本文档

## 关键设计决策

### 1. 球的物理参数
选择标准足球的参数(半径11cm,质量450g)以保证真实性。弹性系数设置为0.7以允许一定的反弹但不过度。

### 2. 奖励函数设计
采用多阶段奖励策略:
- 接近阶段: `approach_ball`
- 接触阶段: `ball_contact`
- 踢球阶段: `kick_ball_velocity`, `kick_ball_to_target`
- 约束: `kick_ball_height`

这样的设计有助于课程学习,机器人会逐步学会完整的踢球动作。

### 3. 观测空间
将球的位置和速度转换到机器人坐标系,使得策略更容易学习(与机器人的朝向无关)。

### 4. 终止条件
允许机器人身体降低到0.3米(原本0.2米),以便执行踢球前的准备动作。

## 测试建议

### 1. 功能测试
```bash
# 测试环境是否能正常加载
python humanoidverse/train_agent.py exp=soccer_kick robot=g1_29dof simulator=isaacsim num_envs=1 headless=False max_iterations=10
```

### 2. 奖励调试
在训练初期监控以下指标:
- `approach_ball`: 应该在前几百次迭代中增加
- `ball_contact`: 应该在1000次迭代左右开始出现
- `kick_ball_velocity`: 应该在2000次迭代后开始增加
- `kick_ball_to_target`: 应该在3000次迭代后开始显著增加

### 3. 可视化检查
使用 `headless=False` 运行几个环境,观察:
- 球是否正确生成在机器人前方
- 球是否与地面和机器人正确碰撞
- 球被踢后的运动是否符合物理规律

## 已知限制和未来改进

### 当前限制
1. 只有一个球,没有多球训练
2. 没有对手或障碍物
3. 球的位置是固定分布,缺少多样性
4. 没有使用视觉输入
5. 目标位置是固定的

### 改进方向
1. **多球训练**: 让机器人学会选择和踢不同的球
2. **动态目标**: 目标位置可以变化,训练瞄准能力
3. **守门员**: 添加对抗性训练
4. **视觉输入**: 使用相机观测球的位置而非直接状态
5. **课程学习**: 实现自动课程学习,逐步增加难度
6. **连续踢球**: 学习多次触球和控球
7. **不同地形**: 在不同地面材质上训练
8. **传球协作**: 多机器人协作训练

## 注意事项

1. **训练时间**: 踢球是复杂的全身协调任务,预计需要10-20M步才能学到基本的踢球动作
2. **超参数调整**: 可能需要根据实际训练效果调整奖励权重
3. **参考动作**: 强烈建议使用包含踢球动作的参考motion作为初始化
4. **稳定性**: 注意监控机器人的稳定性,避免过度追求踢球力度而导致摔倒

## 联系信息

如有问题或建议,请参考代码中的注释或提交Issue。

---
实现者: AI Assistant
日期: 2026年1月13日
