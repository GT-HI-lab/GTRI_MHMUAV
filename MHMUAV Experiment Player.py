import pygame
import cv2 as cv
from pylsl import StreamInfo, StreamOutlet
import time


class ExperimentPlayer:
    def __init__(self):
        """Initialize the experiment player."""
        pygame.init()
        pygame.display.init()

        # Setup LSL stream
        self.outlet = self._setup_lsl()

        # Create fullscreen window with double buffering for smoother display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption("Press ENTER to start, Q to quit")

        # Define video paths and possible orders
        self.video_paths = {
            'unreliable': "/Users/debbiehsu/Documents/HI Lab/MHMUAV Video Overlay/Both Unreliable.mp4",
            'reliable': "/Users/debbiehsu/Documents/HI Lab/MHMUAV Video Overlay/Both Reliable.mp4",
            'mix': "/Users/debbiehsu/Documents/HI Lab/MHMUAV Video Overlay/Mixed.mp4"
        }

        # Pre-define all possible orders
        self.orders = [
            ('unreliable', 'reliable', 'mix'),
            ('unreliable', 'mix', 'reliable'),
            ('reliable', 'unreliable', 'mix'),
            ('reliable', 'mix', 'unreliable'),
            ('mix', 'unreliable', 'reliable'),
            ('mix', 'reliable', 'unreliable')
        ]

    def _setup_lsl(self):
        """Setup LSL stream for markers with wall clock time."""
        # Import the specific constants from pylsl
        from pylsl import cf_double64

        # Configure stream to match EmotiBit's expected parameters exactly
        # Name: 'DataSyncMarker', sourceId: '12345'
        info = StreamInfo('DataSyncMarker', 'Markers', 2, 0, cf_double64, '12345')

        # Add additional metadata if needed
        info_desc = info.desc()
        info_desc.append_child_value("manufacturer", "Custom")

        return StreamOutlet(info)

    def get_participant_id(self):
        """Get participant ID from user input."""
        font = pygame.font.Font(None, 74)
        input_text = ""

        while True:
            self.screen.fill((0, 0, 0))

            # Show prompts
            prompt = font.render("Enter Session ID:", True, (255, 255, 255))
            text_surface = font.render(input_text, True, (255, 255, 255))
            instruction = font.render("Press ENTER when done", True, (255, 255, 255))

            # Position text
            self.screen.blit(prompt, (self.screen.get_width() // 2 - prompt.get_width() // 2, 200))
            self.screen.blit(text_surface, (self.screen.get_width() // 2 - text_surface.get_width() // 2, 300))
            self.screen.blit(instruction, (self.screen.get_width() // 2 - instruction.get_width() // 2, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and input_text:
                        return input_text
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode

    def wait_for_enter(self):
        """Wait for ENTER key to start or 'q' to quit."""
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.event.clear()

        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_q:
                    return False

    def play_video(self, video_file):
        """Play a single video and handle LSL markers."""
        try:
            cap = cv.VideoCapture(video_file)
            if not cap.isOpened():
                return False

            # Get video properties
            fps = cap.get(cv.CAP_PROP_FPS)
            frame_time = 1 / fps

            # Send start marker with wall clock time
            self.outlet.push_sample([1, time.time()])

            clock = pygame.time.Clock()
            last_frame_time = time.time()

            while cap.isOpened():
                current_time = time.time()

                # Only process frame if enough time has passed
                if current_time - last_frame_time >= frame_time:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Process and display frame
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    frame = cv.resize(frame, (self.screen.get_width(), self.screen.get_height()))
                    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

                    self.screen.blit(frame, (0, 0))
                    pygame.display.flip()

                    last_frame_time = current_time

                # Check for quit
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        cap.release()
                        return False

                # Control frame rate
                clock.tick(fps)

            # Send end marker with wall clock time
            self.outlet.push_sample([2, time.time()])
            cap.release()

            self.screen.fill((0, 0, 0))
            pygame.display.flip()

            return True

        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def run_experiment(self):
        """Run the complete experiment."""
        try:
            # Get participant ID and determine video order
            participant_id = self.get_participant_id()
            order_index = (int(participant_id) - 1) % len(self.orders)
            video_order = self.orders[order_index]

            print(f"Participant ID: {participant_id}")
            print(f"Video order: {video_order}")

            # Play videos in order
            for video_name in video_order:
                if not self.wait_for_enter():
                    break
                if not self.play_video(self.video_paths[video_name]):
                    break

        finally:
            pygame.quit()


def main():
    player = ExperimentPlayer()
    player.run_experiment()


if __name__ == "__main__":
    main()
