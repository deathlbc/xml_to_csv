from chardet.universaldetector import UniversalDetector
import re

def detect_encode_auto(source_file):
    detector = UniversalDetector()
    detector.reset()
    
    with open(source_file, 'rb') as f:
        for row in f:
            detector.feed(row)
            if detector.done:
                break
    detector.close()

    return detector.result['encoding']
