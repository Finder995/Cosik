"""
Voice Recognition Module for Cosik AI Agent.

Features:
- Speech-to-text conversion
- Real-time voice commands
- Multiple language support
- Microphone input handling
- Voice activity detection
- Command processing from speech
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from loguru import logger
import asyncio

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not available. Install with: pip install SpeechRecognition pyaudio")


class VoiceRecognitionModule:
    """
    Voice recognition module for speech-to-text and voice commands.
    
    Features:
    - Speech recognition
    - Real-time listening
    - Command detection
    - Multi-language support
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize voice recognition module.
        
        Args:
            config: Module configuration
        """
        self.config = config
        self.voice_config = config.get('voice', {})
        
        # Speech recognizer
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        
        # Microphone
        self.microphone = None
        
        # Recognition settings
        self.language = self.voice_config.get('language', 'pl-PL')
        self.energy_threshold = self.voice_config.get('energy_threshold', 4000)
        self.pause_threshold = self.voice_config.get('pause_threshold', 0.8)
        
        # Command callbacks
        self.command_callbacks = []
        
        # Recognition history
        self.history = []
        self.max_history = 100
        
        # Listening state
        self.is_listening = False
        self.background_listener = None
        
        if self.recognizer:
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.pause_threshold = self.pause_threshold
        
        logger.info("Voice recognition module initialized")
    
    async def recognize_from_microphone(self, duration: Optional[int] = None,
                                       timeout: int = 5) -> Dict[str, Any]:
        """
        Recognize speech from microphone.
        
        Args:
            duration: Recording duration in seconds (None for automatic)
            timeout: Timeout waiting for speech
            
        Returns:
            Recognition result
        """
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speech recognition not available'
                }
            
            with sr.Microphone() as source:
                logger.info("Listening...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for speech
                if duration:
                    audio = self.recognizer.record(source, duration=duration)
                else:
                    audio = self.recognizer.listen(source, timeout=timeout)
                
                logger.info("Processing speech...")
                
                # Recognize speech
                text = self._recognize_audio(audio)
                
                if text:
                    # Add to history
                    self._add_to_history({
                        'timestamp': datetime.now().isoformat(),
                        'text': text,
                        'language': self.language,
                        'source': 'microphone'
                    })
                    
                    logger.info(f"Recognized: {text}")
                    return {
                        'success': True,
                        'text': text,
                        'language': self.language
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Could not understand audio'
                    }
        
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'error': 'Timeout waiting for speech'
            }
        except Exception as e:
            logger.error(f"Recognition from microphone failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def recognize_from_file(self, audio_file: str) -> Dict[str, Any]:
        """
        Recognize speech from audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Recognition result
        """
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speech recognition not available'
                }
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            text = self._recognize_audio(audio)
            
            if text:
                self._add_to_history({
                    'timestamp': datetime.now().isoformat(),
                    'text': text,
                    'language': self.language,
                    'source': audio_file
                })
                
                logger.info(f"Recognized from file: {text}")
                return {
                    'success': True,
                    'text': text,
                    'file': audio_file
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not understand audio'
                }
        
        except Exception as e:
            logger.error(f"Recognition from file failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _recognize_audio(self, audio) -> Optional[str]:
        """
        Recognize audio using Google Speech Recognition.
        
        Args:
            audio: Audio data
            
        Returns:
            Recognized text or None
        """
        try:
            # Try Google Speech Recognition first (free)
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            
            # Fallback to Sphinx (offline)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except:
                return None
    
    async def start_listening(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Start continuous listening mode.
        
        Args:
            callback: Function to call with recognized text
            
        Returns:
            Start result
        """
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Speech recognition not available'
                }
            
            if self.is_listening:
                return {
                    'success': False,
                    'error': 'Already listening'
                }
            
            def audio_callback(recognizer, audio):
                """Callback for background listening."""
                try:
                    text = self._recognize_audio(audio)
                    if text:
                        # Add to history
                        self._add_to_history({
                            'timestamp': datetime.now().isoformat(),
                            'text': text,
                            'language': self.language,
                            'source': 'continuous'
                        })
                        
                        logger.info(f"Heard: {text}")
                        
                        # Call user callback
                        if callback:
                            asyncio.create_task(callback(text))
                        
                        # Process command callbacks
                        for cmd_callback in self.command_callbacks:
                            asyncio.create_task(cmd_callback(text))
                
                except Exception as e:
                    logger.error(f"Audio callback error: {e}")
            
            # Start background listening
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            self.background_listener = self.recognizer.listen_in_background(
                self.microphone,
                audio_callback,
                phrase_time_limit=10
            )
            
            self.is_listening = True
            
            logger.info("Started continuous listening")
            return {
                'success': True,
                'mode': 'continuous'
            }
        
        except Exception as e:
            logger.error(f"Start listening failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_listening(self) -> Dict[str, Any]:
        """Stop continuous listening mode."""
        try:
            if not self.is_listening:
                return {
                    'success': False,
                    'error': 'Not currently listening'
                }
            
            if self.background_listener:
                self.background_listener(wait_for_stop=False)
                self.background_listener = None
            
            self.is_listening = False
            
            logger.info("Stopped continuous listening")
            return {
                'success': True
            }
        
        except Exception as e:
            logger.error(f"Stop listening failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def register_command_callback(self, callback: Callable):
        """
        Register callback for voice commands.
        
        Args:
            callback: Async function to call with recognized text
        """
        self.command_callbacks.append(callback)
        logger.info("Command callback registered")
    
    def _add_to_history(self, entry: Dict[str, Any]):
        """Add recognition to history."""
        self.history.append(entry)
        
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    async def get_history(self, limit: int = 20) -> Dict[str, Any]:
        """Get recognition history."""
        try:
            recent = self.history[-limit:]
            
            return {
                'success': True,
                'history': recent,
                'count': len(recent)
            }
        
        except Exception as e:
            logger.error(f"Get history failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def clear_history(self) -> Dict[str, Any]:
        """Clear recognition history."""
        try:
            count = len(self.history)
            self.history = []
            
            return {
                'success': True,
                'cleared': count
            }
        
        except Exception as e:
            logger.error(f"Clear history failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def set_language(self, language: str) -> Dict[str, Any]:
        """
        Set recognition language.
        
        Args:
            language: Language code (e.g., 'en-US', 'pl-PL')
            
        Returns:
            Result
        """
        try:
            self.language = language
            
            logger.info(f"Language set to: {language}")
            return {
                'success': True,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"Set language failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            'available': SPEECH_RECOGNITION_AVAILABLE,
            'is_listening': self.is_listening,
            'language': self.language,
            'history_count': len(self.history),
            'callbacks_registered': len(self.command_callbacks)
        }


# For plugin compatibility
class VoiceRecognitionPlugin:
    """Voice recognition plugin wrapper."""
    
    def __init__(self, config: Dict[str, Any]):
        self.module = VoiceRecognitionModule(config)
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        action = kwargs.pop('action', 'recognize')
        
        if action == 'recognize':
            return await self.module.recognize_from_microphone(**kwargs)
        elif action == 'recognize_file':
            return await self.module.recognize_from_file(**kwargs)
        elif action == 'start_listening':
            return await self.module.start_listening(**kwargs)
        elif action == 'stop_listening':
            return await self.module.stop_listening()
        elif action == 'history':
            return await self.module.get_history(**kwargs)
        elif action == 'clear_history':
            return await self.module.clear_history()
        elif action == 'set_language':
            return await self.module.set_language(**kwargs)
        elif action == 'status':
            return {'success': True, 'status': self.module.get_status()}
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            'name': 'voice',
            'version': '1.0.0',
            'description': 'Voice recognition and speech-to-text',
            'actions': [
                'recognize', 'recognize_file', 'start_listening',
                'stop_listening', 'history', 'clear_history',
                'set_language', 'status'
            ],
            'languages': ['en-US', 'pl-PL', 'de-DE', 'fr-FR', 'es-ES']
        }


# Plugin metadata
PLUGIN_INFO = {
    'name': 'voice',
    'version': '1.0.0',
    'class': VoiceRecognitionPlugin,
    'description': 'Voice recognition and speech commands',
    'author': 'Finder995',
    'requires': ['SpeechRecognition', 'pyaudio']
}
