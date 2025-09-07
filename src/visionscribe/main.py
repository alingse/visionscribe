#!/usr/bin/env python3
"""
VisionScribe - Video to Code / Video to Documentation Converter

Command-line interface for converting videos to code projects or documentation.
"""

import click
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .video_processor import VideoProcessor
from .text_extractor import TextExtractor
from .text_deduplicator import TextDeduplicator
from .ai_reconstructor import AIReconstructor
from .output_generator import OutputGenerator


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """VisionScribe - Convert videos to code projects or documentation."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path), default="./output")
@click.option("--format", "-f", type=click.Choice(["code", "docs", "both"]), default="code", help="Output format")
@click.option("--fps", default=1, help="Frame extraction FPS")
@click.option("--languages", default="en,zh", help="OCR languages")
@click.option("--model", default="gpt-4", help="AI model to use")
@click.option("--openai-api-key", help="OpenAI API key")
def run(input_file: Path, output_dir: Path, format: str, fps: int, 
         languages: str, model: str, openai_api_key: Optional[str]) -> None:
    """Convert video to code/docs in one command.
    
    This is the main command for automatic video processing. Just specify
    the input video file and output directory, and VisionScribe will:
    1. Extract frames from the video
    2. Extract text using OCR
    3. Remove duplicates
    4. Use AI to reconstruct project structure
    5. Generate code and/or documentation
    
    Example: visionscribe run tutorial.mp4 ./project-output
    """
    try:
        click.echo(f"🎬 Starting video processing...")
        click.echo(f"📹 Input: {input_file}")
        click.echo(f"📁 Output: {output_dir}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processors
        click.echo("⚙️  Initializing processors...")
        video_processor = VideoProcessor()
        text_extractor = TextExtractor(languages=languages.split(","))
        text_deduplicator = TextDeduplicator()
        ai_reconstructor = AIReconstructor(provider="openai", api_key=openai_api_key, model=model)
        output_generator = OutputGenerator()
        
        # Process video
        click.echo("🎬 Extracting frames...")
        frames = video_processor.extract_frames(str(input_file), fps)
        click.echo(f"✅ Extracted {len(frames)} frames")
        
        # Extract text
        click.echo("🔤 Extracting text...")
        text_blocks = text_extractor.extract_text_from_video(frames)
        click.echo(f"✅ Extracted {len(text_blocks)} text blocks")
        
        # Deduplicate text
        click.echo("🧹 Removing duplicates...")
        unique_texts = text_deduplicator.deduplicate_texts(text_blocks)
        click.echo(f"✅ Reduced to {len(unique_texts)} unique texts")
        
        # AI reconstruction
        click.echo("🤖 Reconstructing project...")
        project_data = ai_reconstructor.reconstruct_project(unique_texts)
        click.echo("✅ Project reconstruction completed")
        
        # Generate output
        if format in ["code", "both"]:
            click.echo("💻 Generating code...")
            code_output = output_dir / "code"
            output_generator.generate_codebase(project_data, str(code_output))
            click.echo(f"✅ Code generated in {code_output}")
        
        if format in ["docs", "both"]:
            click.echo("📄 Generating documentation...")
            doc_output = output_dir / "docs.md"
            output_generator.generate_documentation(project_data, str(doc_output))
            click.echo(f"✅ Documentation generated: {doc_output}")
        
        click.echo(f"🎉 Processing completed! Check {output_dir} for results.")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
def init(input_dir: Path) -> None:
    """Initialize a new VisionScribe project.
    
    Creates configuration files and templates for a new project.
    
    Example: visionscribe init ./my-project
    """
    try:
        import json
        
        # Create sample configuration
        config = {
            "video": {
                "fps": 1,
                "quality": 95,
                "max_frames": 1000
            },
            "ocr": {
                "languages": ["en", "zh"],
                "confidence_threshold": 0.8
            },
            "ai": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7
            }
        }
        
        config_path = input_dir / "visionscribe.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create environment file
        env_content = """# VisionScribe Configuration
OPENAI_API_KEY=your_openai_api_key_here
"""
        env_path = input_dir / ".env"
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        click.echo(f"📁 Configuration created in {input_dir}:")
        click.echo(f"  📄 visionscribe.json: Project configuration")
        click.echo(f"  🔑 .env: Environment variables")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--fps", default=1, help="Frame extraction FPS")
@click.option("--dedup", is_flag=True, help="Enable frame deduplication")
def frames(input_file: Path, output_dir: Path, fps: int, dedup: bool) -> None:
    """Extract frames from video with timestamp info.
    
    Stage 1: Extract key frames from video and save as timestamped images.
    
    This command analyzes video content and extracts frames at specified intervals,
    removing duplicates if enabled. Each frame is saved with timestamp metadata.
    The frames are saved in a 'frames' subdirectory with timestamp-based naming.
    
    Example: visionscribe frames tutorial.mp4 ./output-dir
    """
    try:
        video_processor = VideoProcessor()
        click.echo(f"🎬 Extracting frames from {input_file} at {fps} FPS...")
        
        frames = video_processor.extract_frames(str(input_file), fps)
        
        # Apply deduplication if requested
        if dedup:
            click.echo("🧹 Removing duplicate frames...")
            frames = video_processor.deduplicate_frames(frames)
        
        # Create frames directory
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Save frames with metadata
        metadata = []
        for i, frame in enumerate(frames):
            timestamp = frame.timestamp if hasattr(frame, 'timestamp') else i / fps
            
            # Convert timestamp to time format (HH:MM:SS.mmm)
            hours = int(timestamp // 3600)
            minutes = int((timestamp % 3600) // 60)
            seconds = int(timestamp % 60)
            milliseconds = int((timestamp % 1) * 1000)
            
            # Create filename with sequential number and timestamp
            time_str = f"{hours:02d}{minutes:02d}{seconds:02d}_{milliseconds:03d}"
            frame_path = frames_dir / f"frame_{i:04d}_{time_str}.jpg"
            
            # Save frame
            img = Image.open(frame.image_path) if hasattr(frame, 'image_path') else frame
            img.save(str(frame_path))
            
            # Store metadata
            metadata.append({
                "frame_id": i,
                "file_path": str(frame_path),
                "timestamp": timestamp,
                "time_format": f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}",
                "size": img.size if hasattr(img, 'size') else (0, 0)
            })
        
        # Save metadata JSON
        metadata_file = frames_dir / "frames_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        click.echo(f"✅ 共切分了 {len(frames)} 个图片")
        click.echo(f"📁 图片保存在: {frames_dir}")
        click.echo(f"📄 元数据保存在: {metadata_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("frames_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default="./ocr_data.json", help="Output JSON file", type=click.Path(path_type=Path))
@click.option("--languages", default="en,zh", help="OCR languages")
@click.option("--confidence", default=0.8, type=float, help="Minimum confidence threshold")
def ocr(frames_dir: Path, output: Path, languages: str, confidence: float) -> None:
    """Extract text from frames and create structured JSON.
    
    Stage 2: Perform OCR on extracted frames and create comprehensive JSON data.
    
    This command processes all image frames in the specified directory, extracts
    text using OCR, and creates a structured JSON file with all frame and text data.
    
    Example: visionscribe ocr ./extracted-frames ./ocr-output.json
    """
    try:
        import cv2
        
        text_extractor = TextExtractor(languages=languages.split(","))
        click.echo(f"🔤 Processing frames in {frames_dir}...")
        
        # Get all image files
        image_files = list(frames_dir.glob("*.jpg")) + list(frames_dir.glob("*.png"))
        
        frames = []
        for img_path in image_files:
            frame = cv2.imread(str(img_path))
            if frame is not None:
                frames.append((img_path, frame))
        
        if not frames:
            click.echo("❌ No frames found in directory", err=True)
            sys.exit(1)
        
        click.echo(f"📹 Found {len(frames)} image frames")
        
        # Process frames with OCR
        ocr_data = []
        for img_path, frame in frames:
            click.echo(f"🔤 Processing {img_path.name}...")
            
            text_blocks = text_extractor.extract_text_from_video([frame])
            
            # Extract timestamp from filename if available
            timestamp = 0.0
            if "t" in img_path.name:
                try:
                    timestamp = float(img_path.name.split("_t")[-1].split(".")[0])
                except:
                    pass
            
            frame_data = {
                "file_path": str(img_path),
                "timestamp": timestamp,
                "text_blocks": []
            }
            
            for block in text_blocks:
                if block["confidence"] >= confidence:
                    frame_data["text_blocks"].append({
                        "text": block["text"],
                        "confidence": block["confidence"],
                        "bbox": block["bbox"],
                        "language": block.get("language", "en")
                    })
            
            ocr_data.append(frame_data)
        
        # Save comprehensive OCR data
        with open(output, 'w', encoding='utf-8') as f:
            json.dump({
                "total_frames": len(ocr_data),
                "processing_info": {
                    "languages": languages.split(","),
                    "confidence_threshold": confidence,
                    "created_at": str(Path().cwd())
                },
                "frames": ocr_data
            }, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ OCR data saved to {output}")
        click.echo(f"📊 Processed {len(ocr_data)} frames with text")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_json", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default="./ai_analysis.json", help="Output JSON file", type=click.Path(path_type=Path))
@click.option("--model", default="gpt-4", help="AI model to use")
@click.option("--openai-api-key", help="OpenAI API key")
@click.option("--dedup", is_flag=True, help="Enable text deduplication")
def analyze(input_json: Path, output: Path, model: str, openai_api_key: Optional[str], dedup: bool) -> None:
    """Analyze and deduplicate OCR data using AI.
    
    Stage 3: AI-powered analysis and deduplication of extracted text data.
    
    This command takes the comprehensive OCR JSON data, uses AI to analyze content,
    remove duplicates, and create a refined structured dataset for project reconstruction.
    
    Example: visionscribe analyze ./ocr-data.json ./analyzed-data.json
    """
    try:
        import json
        
        click.echo(f"🧠 Loading OCR data from {input_json}...")
        
        # Load OCR data
        with open(input_json, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        click.echo(f"📊 Loaded {ocr_data.get('total_frames', 0)} frames")
        
        # Extract all text data
        all_texts = []
        for frame in ocr_data.get('frames', []):
            for text_block in frame.get('text_blocks', []):
                all_texts.append({
                    "text": text_block["text"],
                    "confidence": text_block["confidence"],
                    "timestamp": frame["timestamp"],
                    "source_file": frame["file_path"],
                    "language": text_block.get("language", "en")
                })
        
        click.echo(f"📝 Found {len(all_texts)} text blocks")
        
        # Apply deduplication if requested
        if dedup:
            click.echo("🧹 Removing duplicate texts...")
            text_deduplicator = TextDeduplicator()
            # Convert to dict format for deduplication
            text_dicts = []
            for text_item in all_texts:
                text_dicts.append({
                    "text": text_item["text"],
                    "confidence": text_item["confidence"],
                    "bbox": (0, 0, 100, 50),  # Placeholder
                    "source_frames": [text_item["timestamp"]],
                    "language": text_item["language"]
                })
            
            deduplicated_texts = text_deduplicator.deduplicate_texts(text_dicts)
            
            # Convert back to original format
            refined_texts = []
            for dedup_text in deduplicated_texts:
                refined_texts.append({
                    "text": dedup_text["text"],
                    "confidence": dedup_text["confidence"],
                    "timestamp": dedup_text["source_frames"][0] if dedup_text["source_frames"] else 0,
                    "source_file": "unknown",
                    "language": dedup_text.get("language", "en")
                })
            
            all_texts = refined_texts
            click.echo(f"✅ Reduced to {len(all_texts)} unique texts")
        
        # AI analysis and project reconstruction
        click.echo("🤖 Performing AI analysis...")
        ai_reconstructor = AIReconstructor(provider="openai", api_key=openai_api_key, model=model)
        project_data = ai_reconstructor.reconstruct_project(all_texts)
        
        # Create refined analysis output
        analysis_result = {
            "total_original_texts": len(all_texts) if 'all_texts' in locals() else ocr_data.get('total_frames', 0),
            "analysis_metadata": {
                "model_used": model,
                "ai_provider": "openai",
                "created_at": str(Path().cwd()),
                "deduplication_enabled": dedup
            },
            "refined_texts": [
                {
                    "text": text["text"],
                    "confidence": text["confidence"],
                    "timestamp": text["timestamp"],
                    "language": text.get("language", "en")
                } for text in all_texts
            ],
            "project_structure": project_data.to_dict() if hasattr(project_data, 'to_dict') else str(project_data)
        }
        
        # Save analysis results
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ AI analysis saved to {output}")
        click.echo(f"🎯 Generated {len(all_texts)} refined text entries")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_json", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option("--format", "-f", type=click.Choice(["code", "docs", "both"]), default="code", help="Output format")
@click.option("--model", default="gpt-4", help="AI model to use")
@click.option("--openai-api-key", help="OpenAI API key")
def build(input_json: Path, output_dir: Path, format: str, model: str, openai_api_key: Optional[str]) -> None:
    """Build project files from analyzed JSON data.
    
    Stage 4: Generate actual project files from refined JSON analysis.
    
    This command takes the AI-analyzed JSON data and reconstructs the actual
    project files, including code generation and documentation creation.
    
    Example: visionscribe build ./ai-analysis.json ./final-project
    """
    try:
        import json
        
        click.echo(f"🏗️  Building project from {input_json}...")
        
        # Load analysis data
        with open(input_json, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        click.echo(f"📊 Loaded analysis with {len(analysis_data.get('refined_texts', []))} text entries")
        
        # Initialize components
        ai_reconstructor = AIReconstructor(provider="openai", api_key=openai_api_key, model=model)
        output_generator = OutputGenerator()
        
        # Reconstruct project from refined data
        click.echo("🤖 Reconstructing project structure...")
        
        # Convert refined texts back to format expected by reconstructors
        text_blocks = []
        for i, text_item in enumerate(analysis_data.get('refined_texts', [])):
            text_blocks.append({
                "text": text_item["text"],
                "confidence": text_item["confidence"],
                "bbox": (0, 0, 100, 50),  # Placeholder
                "source_frames": [text_item["timestamp"]],
                "language": text_item.get("language", "en")
            })
        
        project_data = ai_reconstructor.reconstruct_project(text_blocks)
        click.echo("✅ Project structure reconstructed")
        
        # Generate output files
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format in ["code", "both"]:
            click.echo("💻 Generating code files...")
            code_output = output_dir / "code"
            output_generator.generate_codebase(project_data, str(code_output))
            click.echo(f"✅ Code generated in {code_output}")
        
        if format in ["docs", "both"]:
            click.echo("📄 Generating documentation...")
            doc_output = output_dir / "docs.md"
            output_generator.generate_documentation(project_data, str(doc_output))
            click.echo(f"✅ Documentation generated: {doc_output}")
        
        # Save summary
        summary = {
            "source_file": str(input_json),
            "output_directory": str(output_dir),
            "format": format,
            "files_generated": len(project_data.root.files) if hasattr(project_data, 'root') else 0,
            "created_at": str(Path().cwd())
        }
        
        summary_file = output_dir / "build_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        click.echo(f"🎉 Project building completed!")
        click.echo(f"📁 Output directory: {output_dir}")
        click.echo(f"📊 Build summary: {summary_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()