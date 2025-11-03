# ------------------------------------------------------------------------------
# Unit Tests for Zone Mapper
# ------------------------------------------------------------------------------

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.navigation.detector import Detection
from src.navigation.zone_mapper import ZoneMapper
from src.navigation import config


class TestZoneMapper(unittest.TestCase):
    """Test zone mapping logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mapper = ZoneMapper(frame_width=640)
    
    def test_zone_boundaries(self):
        """Test zone boundary calculations"""
        self.assertEqual(self.mapper.frame_width, 640)
        self.assertAlmostEqual(self.mapper.left_boundary, 640 * 0.33, places=1)
        self.assertAlmostEqual(self.mapper.right_boundary, 640 * 0.67, places=1)
    
    def test_get_zone_left(self):
        """Test left zone detection"""
        # Center x = 100 (well within left zone)
        zone = self.mapper.get_zone(100)
        self.assertEqual(zone, 'left')
    
    def test_get_zone_center(self):
        """Test center zone detection"""
        # Center x = 320 (middle of frame)
        zone = self.mapper.get_zone(320)
        self.assertEqual(zone, 'center')
    
    def test_get_zone_right(self):
        """Test right zone detection"""
        # Center x = 550 (well within right zone)
        zone = self.mapper.get_zone(550)
        self.assertEqual(zone, 'right')
    
    def test_get_zone_boundaries(self):
        """Test zone detection at boundaries"""
        # Just before left boundary
        zone = self.mapper.get_zone(self.mapper.left_boundary - 1)
        self.assertEqual(zone, 'left')
        
        # Just after left boundary
        zone = self.mapper.get_zone(self.mapper.left_boundary + 1)
        self.assertEqual(zone, 'center')
        
        # Just before right boundary
        zone = self.mapper.get_zone(self.mapper.right_boundary - 1)
        self.assertEqual(zone, 'center')
        
        # Just after right boundary
        zone = self.mapper.get_zone(self.mapper.right_boundary + 1)
        self.assertEqual(zone, 'right')
    
    def test_get_priority(self):
        """Test priority assignment"""
        # High priority class
        self.assertEqual(self.mapper.get_priority('person'), 10)
        
        # Medium priority class
        self.assertEqual(self.mapper.get_priority('chair'), 3)
        
        # Unknown class (should get priority 0)
        self.assertEqual(self.mapper.get_priority('unknown_object'), 0)
    
    def test_map_detections(self):
        """Test mapping detections to zones"""
        # Create mock detections
        det1 = Detection('person', 0.9, (50, 50, 150, 250))  # left
        det2 = Detection('car', 0.8, (300, 100, 400, 300))   # center
        det3 = Detection('chair', 0.7, (500, 150, 600, 350)) # right
        
        detections = [det1, det2, det3]
        zone_detections = self.mapper.map_detections(detections)
        
        self.assertEqual(len(zone_detections), 3)
        
        # Check zones
        self.assertEqual(zone_detections[0].zone, 'left')
        self.assertEqual(zone_detections[1].zone, 'center')
        self.assertEqual(zone_detections[2].zone, 'right')
        
        # Check priorities
        self.assertEqual(zone_detections[0].priority, 10)  # person
        self.assertEqual(zone_detections[1].priority, 9)   # car
        self.assertEqual(zone_detections[2].priority, 3)   # chair
    
    def test_aggregate_by_zone(self):
        """Test aggregation by zone"""
        # Create detections in different zones
        det1 = Detection('person', 0.9, (50, 50, 150, 250))
        det2 = Detection('person', 0.8, (80, 60, 180, 260))  # Another person in left
        det3 = Detection('car', 0.8, (300, 100, 400, 300))
        
        zone_detections = self.mapper.map_detections([det1, det2, det3])
        aggregated = self.mapper.aggregate_by_zone(zone_detections)
        
        # Check structure
        self.assertIn('left', aggregated)
        self.assertIn('center', aggregated)
        self.assertEqual(len(aggregated['left']), 2)  # Two persons
        self.assertEqual(len(aggregated['center']), 1)  # One car
        
        # Check sorting by priority (should be sorted)
        for zone, dets in aggregated.items():
            priorities = [d.priority for d in dets]
            self.assertEqual(priorities, sorted(priorities, reverse=True))


class TestMessageGeneration(unittest.TestCase):
    """Test message generation logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.navigation.announcer import AudioAnnouncer
        # Disable actual TTS for tests
        self.announcer = AudioAnnouncer(enabled=False)
    
    def test_message_single_object(self):
        """Test message for single object"""
        from src.navigation.zone_mapper import ZoneDetection
        
        det = Detection('person', 0.9, (50, 50, 150, 250))
        zd = ZoneDetection(det, 'left', 10)
        
        message = self.announcer.generate_message({'left': [zd]})
        self.assertEqual(message, "person on your left")
    
    def test_message_multiple_same_class(self):
        """Test message for multiple objects of same class"""
        from src.navigation.zone_mapper import ZoneDetection
        
        det1 = Detection('person', 0.9, (50, 50, 150, 250))
        det2 = Detection('person', 0.8, (80, 60, 180, 260))
        zd1 = ZoneDetection(det1, 'left', 10)
        zd2 = ZoneDetection(det2, 'left', 10)
        
        message = self.announcer.generate_message({'left': [zd1, zd2]})
        self.assertEqual(message, "2 persons on your left")
    
    def test_message_different_zones(self):
        """Test message for objects in different zones"""
        from src.navigation.zone_mapper import ZoneDetection
        
        det1 = Detection('person', 0.9, (50, 50, 150, 250))
        det2 = Detection('car', 0.8, (500, 100, 600, 300))
        zd1 = ZoneDetection(det1, 'left', 10)
        zd2 = ZoneDetection(det2, 'right', 9)
        
        message = self.announcer.generate_message({
            'left': [zd1],
            'right': [zd2]
        })
        self.assertIn('person on your left', message)
        self.assertIn('car on your right', message)
    
    def test_pluralization(self):
        """Test word pluralization"""
        self.assertEqual(self.announcer._pluralize('person'), 'persons')
        self.assertEqual(self.announcer._pluralize('chair'), 'chairs')
        self.assertEqual(self.announcer._pluralize('bus'), 'buses')
        self.assertEqual(self.announcer._pluralize('baby'), 'babies')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestZoneMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageGeneration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
