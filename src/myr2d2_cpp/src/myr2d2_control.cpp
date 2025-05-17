#include <iostream>
#include <chrono>
#include <memory>
#include "sensor_msgs/msg/joint_state.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class Control_R2D2 : public rclcpp::Node
{
    public:
        Control_R2D2(rclcpp::NodeOptions options = rclcpp::NodeOptions())
        : Node("R2D2_Control", options)
        {
            RCLCPP_INFO(this->get_logger(), "R2D2_Control node started");
            joint_pub_ = this->create_publisher<sensor_msgs::msg::JointState>("joint_states1", 1);
            tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
            rate_ = std::make_shared<rclcpp::Rate>(20ms);
            timer_ = this->create_wall_timer(20ms, [this]() { this->timer_callback(); });
            RCLCPP_INFO(this->get_logger(),"R2D2 Control Node launched\n");    
        }
    
        void timer_callback();
        void publish();
    private:
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Rate::SharedPtr rate_;
        rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_pub_;
        std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
        double gripper_extension_;
    };

void Control_R2D2::publish()
{

    sensor_msgs::msg::JointState joint_state;
    geometry_msgs::msg::TransformStamped transformStamped;
    transformStamped.header.stamp = this->get_clock()->now();
    // joint_state.header.stamp = this->get_clock()->now();
    transformStamped.header.frame_id = "base_link";
    transformStamped.child_frame_id = "gripper_pole";
    transformStamped.transform.translation.x = 0.19 + gripper_extension_;
    transformStamped.transform.translation.y = 0.0;
    transformStamped.transform.translation.z = 0.2;
    transformStamped.transform.rotation.x = 0.0;
    transformStamped.transform.rotation.y = 0.0;
    transformStamped.transform.rotation.z = 0.0;
    transformStamped.transform.rotation.w = 1.0;
    // joint_state.name = {"gripper_extension", "left_gripper_joint", "right_gripper_joint"};
    // joint_state.position = {gripper_extension_, 0.0, 0.0};
    RCLCPP_INFO(this->get_logger(),"Gripper Extension Value = %f\n", gripper_extension_);
    transformStamped.transform.rotation.w = 1.0;

    // Set the joint state message
    joint_state.header.stamp = this->now();
    joint_state.name = {"gripper_extension"};
    joint_state.position = {gripper_extension_};

    // Update the gripper extension value
    static bool moving_forward = true;  // Direction flag
    if (moving_forward) {
        gripper_extension_ += 0.0005;  // Move forward
        if (gripper_extension_ >= 0.0) {  // Maximum limit
            moving_forward = false;  // Reverse direction
        }
    } else {
        gripper_extension_ -= 0.0005;  // Move backward
        if (gripper_extension_ <= -0.2) {  // Minimum limit
            moving_forward = true;  // Reverse direction
        }
    }
    
    // tf_broadcaster_->sendTransform(transformStamped);
    joint_pub_->publish(joint_state);
}

void Control_R2D2::timer_callback()
{
    // std::cout << "Timer Called\n";
    this->publish();
}

int main(int argc, char * argv[])
{    
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Control_R2D2>());
    rclcpp::shutdown();
    return 0;
}