# 足球踢球训练快速开始指南

## 5分钟快速开始

### 步骤1: 检查环境

确保你已经安装了所有依赖:
```bash
cd /home/user/ASAP
pip install -r requirements.txt  # 如果有requirements文件
```

### 步骤2: 测试环境(单环境可视化)

```bash
python humanoidverse/train_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=1 \
    headless=False \
    max_iterations=10
```

这将运行10次迭代,你可以看到:
- G1机器人
- 足球在机器人前方
- 目标位置(球门)
- 机器人尝试移动和踢球

### 步骤3: 开始训练(多环境并行)

使用提供的脚本:
```bash
bash scripts/train_soccer_kick.sh
```

或者手动运行:
```bash
python humanoidverse/train_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=4096 \
    headless=True
```

### 步骤4: 监控训练进度

使用TensorBoard:
```bash
tensorboard --logdir=runs/
```

在浏览器中打开 `http://localhost:6006`

关注以下指标:
- `reward/kick_ball_to_target` - 应该逐渐增加
- `reward/approach_ball` - 初期应该很高
- `reward/ball_contact` - 几千次迭代后应该出现
- `episode_length` - 平均回合长度

### 步骤5: 评估训练好的策略

```bash
bash scripts/eval_soccer_kick.sh logs/SoccerKick_G1_Training/model_10000.pt
```

或者手动:
```bash
python humanoidverse/eval_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=1 \
    headless=False \
    checkpoint_path=logs/SoccerKick_G1_Training/model_10000.pt
```

## 常见问题

### Q1: 训练速度很慢怎么办?

**A:** 减少环境数量或使用GPU加速:
```bash
python humanoidverse/train_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=2048 \
    headless=True \
    device=cuda:0
```

### Q2: 机器人总是摔倒?

**A:** 增加稳定性奖励权重,在 `humanoidverse/config/rewards/motion_tracking/reward_soccer_kick.yaml` 中修改:
```yaml
reward_scales:
  teleop_body_position_extend: 1.0  # 增加到1.0
  teleop_body_rotation_extend: 0.5  # 增加到0.5
```

### Q3: 机器人不接近球?

**A:** 增加接近球的奖励:
```yaml
reward_scales:
  approach_ball: 5.0  # 从2.0增加到5.0
```

### Q4: 球飞得太高?

**A:** 增加高度惩罚:
```yaml
reward_scales:
  kick_ball_height: -3.0  # 从-1.0增加到-3.0
```

### Q5: 如何使用参考动作?

**A:** 如果你有踢球的参考动作,在训练配置中指定:
```bash
python humanoidverse/train_agent.py \
    exp=soccer_kick \
    robot=g1_29dof \
    simulator=isaacsim \
    num_envs=4096 \
    headless=True \
    robot.motion.motion_file=path/to/kick_motion.pkl
```

## 训练阶段和预期结果

### 阶段1: 探索 (0-1K iterations)
- 机器人随机移动
- 偶尔会接近球
- `approach_ball` 奖励开始增加

### 阶段2: 接近 (1K-3K iterations)
- 机器人学会走向球
- 开始出现与球的接触
- `ball_contact` 奖励出现

### 阶段3: 接触 (3K-7K iterations)
- 机器人可以稳定接触球
- 球开始移动
- `kick_ball_velocity` 奖励增加

### 阶段4: 踢球 (7K-15K iterations)
- 机器人学会踢球
- 球向目标方向移动
- `kick_ball_to_target` 奖励显著增加

### 阶段5: 精确 (15K+ iterations)
- 踢球动作稳定
- 准确度提高
- 可以考虑增加任务难度

## 高级使用

### 调整球的位置分布

编辑 `humanoidverse/config/env/soccer_kick.yaml`:
```yaml
soccer_ball:
  ball_distance_range: [0.6, 1.5]  # 更大的范围
  ball_lateral_range: [-0.5, 0.5]   # 更大的横向偏移
```

### 使用课程学习

可以手动实现课程学习:

**第一阶段** (0-5K iterations): 球很近
```yaml
ball_distance_range: [0.5, 0.8]
```

**第二阶段** (5K-10K iterations): 球中等距离
```yaml
ball_distance_range: [0.8, 1.2]
```

**第三阶段** (10K+ iterations): 球较远
```yaml
ball_distance_range: [1.0, 1.5]
```

### 添加球的观测到策略输入

如果想让策略直接感知球的位置,在观测配置中添加:

1. 找到你的观测配置文件(或创建新的)
2. 添加球的观测:
```yaml
obs:
  actor_obs:
    # ... 其他观测 ...
    ball_pos_robot_frame: True
    ball_vel_robot_frame: True
```

## 下一步

训练完成后,你可以:

1. **微调**: 调整超参数获得更好的性能
2. **Sim-to-Real**: 准备将策略部署到真实机器人
3. **扩展任务**: 添加更多足球技能(盘带、传球等)
4. **对抗训练**: 添加守门员或对手

## 获取帮助

- 查看详细文档: `SOCCER_KICK_README.md`
- 查看实现细节: `IMPLEMENTATION_SUMMARY.md`
- 查看代码注释: 所有修改的代码都有详细注释

祝训练顺利! ⚽🤖
