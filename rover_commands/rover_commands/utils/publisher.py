import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TrajectoryPublisher(Node):

    def __init__(self):
        super().__init__('trajectory_publisher')
        # Create a publisher of type Twist
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

        self.get_logger().info('Publisher node has been started.')

        # Call the loop to handle user input
        self.cmd_acquisition_loop()

    # Function that prompts user for a direction input and sends the command
    def cmd_acquisition(self, command):
        # Create a Twist message
        twist = Twist()

        # Map input commands to velocity commands
        if command == "w":
            twist.linear.x = 0.5  # Forward
            twist.angular.z = 0.0
        elif command == "s":
            twist.linear.x = -0.5  # Backward
            twist.angular.z = 0.0
        elif command == "a":
            twist.linear.x = 0.0
            twist.angular.z = 0.5  # Turn left
        elif command == "d":
            twist.linear.x = 0.0
            twist.angular.z = -0.5  # Turn right
        elif command == "t":
            twist.linear.x = 0.0  # Stop
            twist.angular.z = 0.0
        elif command == "y":
            twist.linear.x = 0.5  # Forward with turn
            twist.angular.z = 0.5
        else:
            self.get_logger().warn("Invalid command!")
            return

        # Publish the Twist message
        self.publisher_.publish(twist)
        self.get_logger().info(f'Published command: {command}')

    # Loop to handle user input
    def cmd_acquisition_loop(self):
        try:
            while rclpy.ok():
                command = input("Enter command (w/a/s/d/t/y - max 2 characters): ").strip().lower()
                self.cmd_acquisition(command)
        except KeyboardInterrupt:
            self.get_logger().info('Shutting down publisher node.')


def main(args=None):
    rclpy.init(args=args)  # Init ROS python
    node = TrajectoryPublisher()  # Create a Node instance
    try:
        rclpy.spin(node)  # Run the node in a Thread
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()