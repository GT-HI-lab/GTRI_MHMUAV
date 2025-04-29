import pygame
import cv2 as cv
from pylsl import StreamInfo, StreamOutlet
import time
from datetime import datetime


class ExperimentPlayer:
    def __init__(self):
        """Initialize the experiment player."""
        pygame.init()
        pygame.display.init()

        # Setup LSL stream
        self.outlet = self._setup_lsl()

        # Create fullscreen window with double buffering for smoother display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption("Experiment Player")

        # Change file directory 
        # Define video paths and possible orders
        self.video_paths = {
            'unreliable': "file_path_for_Both_Unreliable.mp4",
            'reliable': "file_path_for_Both_Reliable.mp4",
            'mix': "file_path_for_Mixed.mp4"
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
        info = StreamInfo('DataSyncMarker', 'Markers', 2, 0, cf_double64, '12345')

        # Add additional metadata including created_at timestamp
        info_desc = info.desc()
        info_desc.append_child_value("manufacturer", "Custom")

        # Add created_at timestamp to the stream info
        import time
        current_time = time.time()  # Get current Unix timestamp
        info_desc.append_child_value("created_at", str(current_time))

        # Store this timestamp for reference
        self.stream_created_time = current_time

        print(f"LSL Marker Stream Setup:")
        print(f"  Name: DataSyncMarker")
        print(f"  Type: Markers")
        print(f"  Channels: 2 (marker value, wall clock time)")
        print(f"  created_at: {current_time}")

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
            print(f"Attempting to open video file: {video_file}")

            # Check if file exists first
            import os
            if not os.path.exists(video_file):
                print(f"ERROR: Video file does not exist: {video_file}")
                return False

            cap = cv.VideoCapture(video_file)
            if not cap.isOpened():
                print(f"ERROR: Failed to open video file: {video_file}")
                return False

            # Get and display video properties for debugging
            fps = cap.get(cv.CAP_PROP_FPS)
            width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
            frame_count = cap.get(cv.CAP_PROP_FRAME_COUNT)

            print(f"Video properties:")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps}")
            print(f"  Frame count: {frame_count}")
            print(f"  Duration: {frame_count / fps:.2f} seconds")

            frame_time = 1 / fps

            # Read first frame to confirm video can be read
            ret, first_frame = cap.read()
            if not ret:
                print(f"ERROR: Could not read first frame from video file")
                return False

            print(f"Successfully read first frame of size: {first_frame.shape}")

            # Send start marker with wall clock time
            from datetime import datetime
            current_time = time.time()

            self.outlet.push_sample([1, current_time])
            print(f"Sent video start marker with timestamp: {current_time}")
            print(f"Datetime: {datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S.%f')}")

            clock = pygame.time.Clock()
            last_frame_time = time.time()

            # Process first frame
            first_frame = cv.cvtColor(first_frame, cv.COLOR_BGR2RGB)
            first_frame = cv.resize(first_frame, (self.screen.get_width(), self.screen.get_height()))
            first_frame_surface = pygame.surfarray.make_surface(first_frame.swapaxes(0, 1))
            self.screen.blit(first_frame_surface, (0, 0))
            pygame.display.flip()

            frame_count = 1
            print(f"Starting video playback loop")

            # Variable to track early termination
            early_end = False

            while cap.isOpened():
                current_time = time.time()

                # Only process frame if enough time has passed
                if current_time - last_frame_time >= frame_time:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"Reached end of video after {frame_count} frames")
                        break

                    # Process and display frame
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    frame = cv.resize(frame, (self.screen.get_width(), self.screen.get_height()))
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

                    self.screen.blit(frame_surface, (0, 0))
                    pygame.display.flip()

                    last_frame_time = current_time
                    frame_count += 1

                    # Print progress every 100 frames
                    if frame_count % 100 == 0:
                        print(f"Played {frame_count} frames")

                # Check for quit or early end
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            print("User pressed Q to quit")
                            cap.release()
                            return False
                        elif event.key == pygame.K_e:
                            print("User pressed E to end video early")
                            early_end = True
                            break

                # Break the playback loop if early end requested
                if early_end:
                    break

                # Control frame rate
                clock.tick(fps)

            # Send end marker with wall clock time
            end_time = time.time()

            # Use a different marker value (3) for early termination
            if early_end:
                self.outlet.push_sample([3, end_time])
                print(f"Sent early video end marker with timestamp: {end_time}")
            else:
                self.outlet.push_sample([2, end_time])
                print(f"Sent video end marker with timestamp: {end_time}")

            print(f"Datetime: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S.%f')}")
            print(f"Video playback duration: {end_time - current_time:.2f} seconds")

            cap.release()
            self.screen.fill((0, 0, 0))

            self.screen.fill((0, 0, 0))
            pygame.display.flip()

            # Small delay to prevent accidental key press from the previous video ending
            pygame.time.delay(1000)

            return True

        except Exception as e:
            print(f"Error in play_video: {str(e)}")
            import traceback
            traceback.print_exc()
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

            # Show blank screen at experiment completion
            self.screen.fill((0, 0, 0))
            pygame.display.flip()

            # Wait for any key to exit
            waiting_for_exit = True
            while waiting_for_exit:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        waiting_for_exit = False
                        break

        finally:
            pygame.quit()


def main():
    player = ExperimentPlayer()
    player.run_experiment()


if __name__ == "__main__":
    main()
