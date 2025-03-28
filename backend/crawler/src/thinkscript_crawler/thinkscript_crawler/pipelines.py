import json
import os
from datetime import datetime

class ThinkscriptPipeline:
    def __init__(self):
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Initialize output file
        self.file = open('output/thinkscript_data.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def process_item(self, item, spider):
        """Process each item and write to file."""
        # Convert item to JSON string
        line = json.dumps(dict(item), ensure_ascii=False)
        
        # Add comma if not first item
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
            
        # Write item to file
        self.file.write(line)
        
        return item

    def close_spider(self, spider):
        """Close the output file when spider is closed."""
        self.file.write('\n]')
        self.file.close() 