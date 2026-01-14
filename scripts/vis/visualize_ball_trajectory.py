"""
Visualization script for soccer ball trajectory
Plots the ball's position over time during evaluation
"""

import matplotlib.pyplot as plt
import numpy as np
import torch
import argparse
from pathlib import Path


def visualize_ball_trajectory(log_file):
    """
    Visualize the trajectory of the soccer ball from a log file
    
    Args:
        log_file: Path to the log file containing ball positions
    """
    # Load the log file (assuming it's saved as numpy or torch tensor)
    if log_file.endswith('.npy'):
        data = np.load(log_file, allow_pickle=True).item()
    elif log_file.endswith('.pt'):
        data = torch.load(log_file)
    else:
        raise ValueError("Unsupported file format. Use .npy or .pt")
    
    # Extract ball positions
    ball_positions = data.get('ball_positions', None)
    if ball_positions is None:
        print("No ball position data found in log file")
        return
    
    # Convert to numpy if needed
    if isinstance(ball_positions, torch.Tensor):
        ball_positions = ball_positions.cpu().numpy()
    
    # Create figure with subplots
    fig = plt.figure(figsize=(15, 5))
    
    # 2D trajectory (top view)
    ax1 = fig.add_subplot(131)
    ax1.plot(ball_positions[:, 0], ball_positions[:, 1], 'b-', linewidth=2, label='Ball path')
    ax1.scatter(ball_positions[0, 0], ball_positions[0, 1], c='green', s=100, label='Start', zorder=5)
    ax1.scatter(ball_positions[-1, 0], ball_positions[-1, 1], c='red', s=100, label='End', zorder=5)
    
    # Add target (goal) position if available
    target_pos = data.get('target_position', None)
    if target_pos is not None:
        if isinstance(target_pos, torch.Tensor):
            target_pos = target_pos.cpu().numpy()
        ax1.scatter(target_pos[0], target_pos[1], c='orange', s=200, marker='*', label='Target', zorder=5)
    
    ax1.set_xlabel('X Position (m)')
    ax1.set_ylabel('Y Position (m)')
    ax1.set_title('Ball Trajectory (Top View)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Height over time
    ax2 = fig.add_subplot(132)
    time_steps = np.arange(len(ball_positions)) * 0.02  # Assuming 50Hz control
    ax2.plot(time_steps, ball_positions[:, 2], 'r-', linewidth=2)
    ax2.axhline(y=0.11, color='k', linestyle='--', alpha=0.3, label='Ground + ball radius')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Height (m)')
    ax2.set_title('Ball Height Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Velocity over time
    ax3 = fig.add_subplot(133)
    ball_velocities = data.get('ball_velocities', None)
    if ball_velocities is not None:
        if isinstance(ball_velocities, torch.Tensor):
            ball_velocities = ball_velocities.cpu().numpy()
        
        speed = np.linalg.norm(ball_velocities, axis=1)
        ax3.plot(time_steps[:len(speed)], speed, 'g-', linewidth=2)
        ax3.axhline(y=2.0, color='k', linestyle='--', alpha=0.3, label='Kick threshold')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Speed (m/s)')
        ax3.set_title('Ball Speed Over Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_file = Path(log_file).parent / f"{Path(log_file).stem}_trajectory.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Trajectory visualization saved to: {output_file}")
    
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Visualize soccer ball trajectory')
    parser.add_argument('log_file', type=str, help='Path to the log file (.npy or .pt)')
    args = parser.parse_args()
    
    visualize_ball_trajectory(args.log_file)


if __name__ == '__main__':
    main()
