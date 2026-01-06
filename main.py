#!/usr/bin/env python3
"""
Gemini Voice Bot - Main Entry Point
Real-time voice assistant for SOP-based question answering in Tanglish
"""
import asyncio
import sys
from pathlib import Path
from loguru import logger
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Import configuration and assistant
from config import Config
from src.voice_assistant import GeminiVoiceAssistant


def setup_logging(config: Config):
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    
    # Add console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        config.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=config.log_level,
        rotation="10 MB",
        retention="7 days"
    )


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🎤  GEMINI VOICE BOT - SOP ASSISTANT  🤖       ║
║                                                           ║
║       Real-time voice interaction in Tanglish            ║
║       Powered by Gemini AI & RAG                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_menu():
    """Print interactive menu"""
    menu = f"""
{Fore.YELLOW}Available Commands:{Style.RESET_ALL}
  {Fore.GREEN}1{Style.RESET_ALL} - Load and index SOP documents
  {Fore.GREEN}2{Style.RESET_ALL} - Ask a text question
  {Fore.GREEN}3{Style.RESET_ALL} - Ask a voice question (from file)
  {Fore.GREEN}4{Style.RESET_ALL} - Start live voice session
  {Fore.GREEN}5{Style.RESET_ALL} - Show system statistics
  {Fore.GREEN}6{Style.RESET_ALL} - Rebuild index (force)
  {Fore.GREEN}q{Style.RESET_ALL} - Quit

"""
    print(menu)


async def main():
    """Main application entry point"""
    print_banner()
    
    # Load configuration
    logger.info("Loading configuration...")
    config = Config()
    
    # Setup logging
    setup_logging(config)
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        logger.error("Configuration errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        
        if not config.google_api_key:
            print(f"\n{Fore.RED}ERROR: GOOGLE_API_KEY not set!{Style.RESET_ALL}")
            print(f"Please set your API key in .env file")
            print(f"Copy .env.example to .env and add your key\n")
            return
    
    # Initialize assistant
    try:
        logger.info("Initializing Gemini Voice Assistant...")
        assistant = GeminiVoiceAssistant(config)
        print(f"{Fore.GREEN}✓ Assistant initialized successfully!{Style.RESET_ALL}\n")
        
        # Auto-load SOPs if folder exists and has files
        if config.sop_folder.exists():
            files = list(config.sop_folder.glob("*"))
            if files:
                print(f"{Fore.CYAN}Found {len(files)} files in SOP folder. Loading...{Style.RESET_ALL}")
                stats = assistant.load_and_index_sops()
                print(f"{Fore.GREEN}✓ Indexed {stats['document_count']} document chunks{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.YELLOW}⚠ SOP folder is empty. Add documents to {config.sop_folder}{Style.RESET_ALL}\n")
        
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {e}")
        print(f"{Fore.RED}ERROR: Failed to initialize assistant{Style.RESET_ALL}")
        return
    
    # Main interaction loop
    while True:
        print_menu()
        choice = input(f"{Fore.CYAN}Enter your choice: {Style.RESET_ALL}").strip().lower()
        
        try:
            if choice == 'q':
                print(f"\n{Fore.YELLOW}Goodbye! 👋{Style.RESET_ALL}\n")
                break
            
            elif choice == '1':
                # Load and index SOPs
                print(f"\n{Fore.CYAN}Loading SOP documents...{Style.RESET_ALL}")
                stats = assistant.load_and_index_sops()
                print(f"{Fore.GREEN}✓ Success!{Style.RESET_ALL}")
                print(f"  Documents indexed: {stats['document_count']}")
                print(f"  Status: {stats['status']}\n")
            
            elif choice == '2':
                # Text question
                print(f"\n{Fore.CYAN}Ask your question:{Style.RESET_ALL}")
                question = input("> ").strip()
                
                if not question:
                    print(f"{Fore.YELLOW}Question empty, skipping...{Style.RESET_ALL}\n")
                    continue
                
                print(f"\n{Fore.CYAN}Processing...{Style.RESET_ALL}")
                response = assistant.process_text_query(question)
                print(f"\n{Fore.GREEN}Response:{Style.RESET_ALL}")
                print(f"{response}\n")
            
            elif choice == '3':
                # Voice question from file
                print(f"\n{Fore.CYAN}Enter path to audio file (WAV format):{Style.RESET_ALL}")
                audio_path_str = input("> ").strip()
                
                audio_path = Path(audio_path_str)
                if not audio_path.exists():
                    print(f"{Fore.RED}File not found: {audio_path}{Style.RESET_ALL}\n")
                    continue
                
                print(f"\n{Fore.CYAN}Processing voice query...{Style.RESET_ALL}")
                transcribed, response = assistant.process_voice_query(audio_path)
                
                print(f"\n{Fore.YELLOW}Transcribed:{Style.RESET_ALL} {transcribed}")
                print(f"\n{Fore.GREEN}Response:{Style.RESET_ALL}")
                print(f"{response}\n")
            
            elif choice == '4':
                # Live voice session
                print(f"\n{Fore.CYAN}Starting live voice session...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Press Ctrl+C to stop the session{Style.RESET_ALL}\n")
                await assistant.start_live_session()
            
            elif choice == '5':
                # System statistics
                print(f"\n{Fore.CYAN}System Statistics:{Style.RESET_ALL}")
                stats = assistant.get_system_stats()
                
                print(f"\n{Fore.GREEN}Configuration:{Style.RESET_ALL}")
                for key, value in stats['config'].items():
                    print(f"  {key}: {value}")
                
                print(f"\n{Fore.GREEN}SOP Documents:{Style.RESET_ALL}")
                for key, value in stats['sop_stats'].items():
                    print(f"  {key}: {value}")
                
                print(f"\n{Fore.GREEN}Retrieval System:{Style.RESET_ALL}")
                for key, value in stats['retrieval_stats'].items():
                    print(f"  {key}: {value}")
                print()
            
            elif choice == '6':
                # Force rebuild index
                print(f"\n{Fore.YELLOW}⚠ This will rebuild the entire index{Style.RESET_ALL}")
                confirm = input("Continue? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    print(f"\n{Fore.CYAN}Rebuilding index...{Style.RESET_ALL}")
                    stats = assistant.load_and_index_sops(force_rebuild=True)
                    print(f"{Fore.GREEN}✓ Index rebuilt successfully!{Style.RESET_ALL}")
                    print(f"  Documents indexed: {stats['document_count']}\n")
                else:
                    print(f"{Fore.YELLOW}Cancelled{Style.RESET_ALL}\n")
            
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}\n")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}\n")
            continue
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application terminated{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)
