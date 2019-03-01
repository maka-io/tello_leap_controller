import sys, thread, time
from datetime import datetime

from LeapSrc import Leap

from TelloSrc.tello import Tello


class TelloLeapListener(Leap.Listener):
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    start_hand_pos = 0
    start_hand_pitch = 0
    start_hand_roll = 0
    start_hand_yaw = 0

    curr_hand_pos = 0
    curr_hand_pitch = 0
    curr_hand_roll = 0
    curr_hand_yaw = 0

    taken_off = False

    tello = Tello()
    
    tello.send_command("command")
    tello.send_command("battery?")
    time.sleep(5)

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            #print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
            #    direction.pitch * Leap.RAD_TO_DEG,
            #    normal.roll * Leap.RAD_TO_DEG,
            #    direction.yaw * Leap.RAD_TO_DEG)

            if self.start_hand_pos == 0:
                self.start_hand_pos = hand.palm_position.y

            if self.start_hand_pitch == 0:
                self.start_hand_pitch = direction.pitch * Leap.RAD_TO_DEG

            if self.start_hand_roll == 0:
                self.start_hand_roll = normal.roll * Leap.RAD_TO_DEG

            if self.start_hand_yaw == 0:
                self.start_hand_yaw = direction.yaw * Leap.RAD_TO_DEG

            self.curr_hand_pos = hand.palm_position.y - self.start_hand_pos
            self.curr_hand_pitch = self.start_hand_pitch - direction.pitch * Leap.RAD_TO_DEG
            self.curr_hand_roll = self.start_hand_roll - normal.roll * Leap.RAD_TO_DEG
            self.curr_hand_yaw = direction.yaw * Leap.RAD_TO_DEG - self.start_hand_yaw

            #print "pos: %f, pitch: %f, roll: %f, yaw: %f" % (
            #        self.curr_hand_pos,
            #        self.curr_hand_pitch,
            #        self.curr_hand_roll,
            #        self.curr_hand_yaw)

            if not (self.taken_off) and self.curr_hand_pos > 10:
                self.tello.send_command("command")
                self.tello.send_command("takeoff")
                self.taken_off = True
                time.sleep(5)

            if self.taken_off and self.curr_hand_pos > 10:
                self.tello.send_command("up %f" % (10))

            if self.taken_off and self.curr_hand_pos < -10:
                self.tello.send_command("down %f" % (10))

            if self.taken_off and self.curr_hand_pitch > 20:
                self.tello.send_command("forward %f" % (10))

            if self.taken_off and self.curr_hand_pitch < -20:
                self.tello.send_command("back %f" % (10))

            if self.taken_off and self.curr_hand_roll > 20:
                self.tello.send_command("right %f" % (10))

            if self.taken_off and self.curr_hand_roll < -20:
                self.tello.send_command("left %f" % (10))

            if self.taken_off and self.curr_hand_yaw > 20:
                self.tello.send_command("cw %f" % (10))

            if self.taken_off and self.curr_hand_yaw < -20:
                self.tello.send_command("ccw %f" % (10))

        if frame.hands.is_empty:
            if self.taken_off:
                self.tello.send_command("command")
                self.tello.send_command("land")
                time.sleep(5)
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

    def get_pos(self):
        return self.curr_hand_pos

    def get_pitch(self):
        return self.curr_hand_pitch

    def get_roll(self):
        return self.curr_hand_roll

    def get_yaw(self):
        return self.curr_hand_yaw


def main():
    # Create a sample listener and controller
    listener = TelloLeapListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()

