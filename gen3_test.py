import time
import sys
import os
import threading

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient

from kortex_api.autogen.messages import Session_pb2, Base_pb2, BaseCyclic_pb2

TIMEOUT_DURATION = 20

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications
    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

def example_angular_action_movement(base):
    
    print("Starting angular action movement ...")
    action = Base_pb2.Action()
    action.name = "Example angular action movement"
    action.application_data = ""

    actuator_count = base.GetActuatorCount()

    # Place arm straight up
    for joint_id in range(actuator_count.count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint_id
        joint_angle.value = 0

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )
    
    print("Executing action")
    base.ExecuteAction(action)

    print("Waiting for movement to finish ...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Angular movement completed")
    else:
        print("Timeout on action notification wait")
    return finished

def get_wrench_feedback(base_cyclic):
    count = 0
    while True:
        feedback = base_cyclic.RefreshFeedback()
        torque = feedback.actuators[5].torque  # NO ATUADOR
        t_e_w_f_x = float(round(feedback.base.tool_external_wrench_force_x, 2))
        t_e_w_f_y = float(round(feedback.base.tool_external_wrench_force_y, 2))
        t_e_w_f_z = float(round(feedback.base.tool_external_wrench_force_z, 2))
        t_e_w_t_x = float(round(feedback.base.tool_external_wrench_torque_x, 2))
        t_e_w_t_y = float(round(feedback.base.tool_external_wrench_torque_y, 2))
        t_e_w_t_z = float(round(feedback.base.tool_external_wrench_torque_z, 2))
        # if count%5 == 0:

        print("force_x:", t_e_w_f_x)
        print("force_y:",t_e_w_f_y)
        print("force_z:",t_e_w_f_z)
        print("torque_x:",t_e_w_t_x)
        print("torque_y:",t_e_w_t_y)
        print("torque_z:",t_e_w_t_z)
        print(" ")
        count += 1
        time.sleep(2)
        os.system('cls')
def cartesian_movement(base, cart):
    action = Base_pb2.Action()
    action.name = "Example Cartesian action movement"
    action.application_data = ""
    cartesian_pose = action.reach_pose.target_pose
    cartesian_pose.x = cart[0]         # (meters)
    cartesian_pose.y = cart[1]    # (meters)
    cartesian_pose.z = cart[2]    # (meters)
    cartesian_pose.theta_x = cart[3] # (degrees)
    cartesian_pose.theta_y = cart[4] # (degrees)
    cartesian_pose.theta_z = cart[5] # (degrees)
    print("1")
    base.ExecuteAction(action)

def example_move_to_home_position(base):
    # Make sure the arm is in Single Level Servoing mode
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)
    
    # Move arm to ready position
    print("Moving the arm to a safe position")
    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
    action_list = base.ReadAllActions(action_type)
    action_handle = None
    for action in action_list.action_list:
        if action.name == "Home":
            action_handle = action.handle

    if action_handle == None:
        print("Can't reach safe position. Exiting")
        return False

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    base.ExecuteActionFromReference(action_handle)
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Safe position reached")
    else:
        print("Timeout on action notification wait")
    return finished
def main():
    # Import the utilities helper module
    import argparse
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parse arguments
    parser = argparse.ArgumentParser()
    args = utilities.parseConnectionArguments(parser)

    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        dicio = {}
        dicio["pivor"] = [0.506, -0.106, 0.08, 177.782, 2.438, 89.477 ]
        dicio["ver"] = [0.414, -0.14, 0.178, 177.559, 2.506, 89.468]
        dicio["conf"] = [0.462, -0.140, 0.043, 175.206, 1.319, 88.93]
        
        # Create required services
        base = BaseClient(router)
        base_cyclic = BaseCyclicClient(router)
        # example_angular_action_movement(base)
        # example_move_to_home_position(base)
        cartesian_movement(base,dicio["pivor"])
        cartesian_movement(base,dicio["conf"])
        cartesian_movement(base,dicio["pivor"])
        #get_wrench_feedback(base_cyclic)



if __name__ == "__main__":
    main()