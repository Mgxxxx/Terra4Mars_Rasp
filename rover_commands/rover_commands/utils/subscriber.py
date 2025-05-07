import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TrajectorySubscriber(Node):

    def __init__(self):
        super().__init__('trajectory_subscriber')
        # Create a subscriber of type Twist, that calls listener_callback
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',  # Topic name
            self.listener_callback,
            10  # Queue size
        )
        self.subscription  # Prevent unused variable warning

        self.get_logger().info('Subscriber node has been started.')
        self.position = {'x': 0.0, 'z': 0.0, 'ry': 0.0}  # Track the robot's position and rotation

    def listener_callback(self, msg):
        # Interpret the received commands
        # Assuming linear.x corresponds to forward/backward movement
        # and angular.z corresponds to rotation around the Z-axis (turning)

        # Update position based on received Twist message
        self.position['x'] += msg.linear.x  # Adjust forward/backward position
        self.position['z'] = msg.linear.z  # Optional, for 3D movement if used
        self.position['ry'] += msg.angular.z  # Adjust rotation around Z-axis (yaw)

        # Log the updated position
        self.get_logger().info(f'Received Twist: linear.x={msg.linear.x}, angular.z={msg.angular.z}')
        self.get_logger().info(f'New Position: {self.position}')

def main(args=None):
    rclpy.init(args=args)
    node = TrajectorySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()