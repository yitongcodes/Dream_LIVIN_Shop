import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  RotateCcw,
  Mic,
  History,
  Dna,
  Globe,
  Rocket,
  Upload,
  Image,
  PenTool,
  X,
  Check,
  Edit3,
  Square,
  Plus,
  Trash2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const App = () => {
  const [feedback, setFeedback] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(() => {
    const saved = localStorage.getItem('dream_livin_status');
    return saved ? JSON.parse(saved) : null;
  });
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('dream_livin_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentView, setCurrentView] = useState('current');
  
  // Voice recording states
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [audioLevels, setAudioLevels] = useState([]);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioChunksRef = useRef([]);
  
  // Image upload states
  const [referenceImages, setReferenceImages] = useState([]);
  const [environmentImage, setEnvironmentImage] = useState(null);
  const [sketchImage, setSketchImage] = useState(null);
  
  // DNA editing state
  const [editingDNA, setEditingDNA] = useState(false);
  const [tempDNA, setTempDNA] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  
  // LIVIN Genome state
  const [livinGenome, setLivinGenome] = useState(() => {
    const saved = localStorage.getItem('dream_livin_genome');
    return saved ? JSON.parse(saved) : {
      round: 0,
      design_summary: '',
      livin_dna: [],
      confirmed_preferences: [],
      rejected_elements: [],
      feedback_history: []
    };
  });
  
  const pollInterval = useRef(null);
  
  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      microphone.connect(analyser);
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setAudioLevels([]);
      visualizeAudio();
    } catch (err) {
      console.error("Error starting recording:", err);
      alert("Failed to start recording. Please check microphone permissions.");
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };
  
  const visualizeAudio = () => {
    if (!analyserRef.current) return;
    
    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    let lastSampleTime = Date.now();
    const sampleInterval = 100;
    
    const updateVisualization = () => {
      if (!analyserRef.current) return;
      
      const now = Date.now();
      if (now - lastSampleTime >= sampleInterval) {
        analyser.getByteFrequencyData(dataArray);
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const average = sum / bufferLength;
        const normalizedLevel = Math.min(average / 128, 1);
        
        setAudioLevels(prev => {
          const newLevels = [...prev, normalizedLevel];
          return newLevels.slice(-100);
        });
        
        lastSampleTime = now;
      }
      
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        animationFrameRef.current = requestAnimationFrame(updateVisualization);
      }
    };
    
    updateVisualization();
  };
  
  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Transcription failed');
      
      const result = await response.json();
      if (result.text) {
        setFeedback(prev => prev + (prev ? ' ' : '') + result.text);
      }
    } catch (err) {
      console.error("Transcription error:", err);
      alert("Failed to transcribe audio. Please try again.");
    } finally {
      setIsTranscribing(false);
    }
  };
  
  // Image handling functions
  const handleReferenceUpload = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      name: file.name
    }));
    setReferenceImages(prev => [...prev, ...newImages].slice(0, 5)); // Max 5 reference images
  };
  
  const handleEnvironmentUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setEnvironmentImage({
        file,
        preview: URL.createObjectURL(file),
        name: file.name
      });
    }
  };
  
  const handleSketchUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSketchImage({
        file,
        preview: URL.createObjectURL(file),
        name: file.name
      });
    }
  };
  
  const removeReferenceImage = (index) => {
    setReferenceImages(prev => prev.filter((_, i) => i !== index));
  };
  
  // DNA editing functions
  const startEditingDNA = () => {
    setTempDNA([...livinGenome.livin_dna]);
    setEditingDNA(true);
  };
  
  const saveDNAEdits = async () => {
    const updatedGenome = { ...livinGenome, livin_dna: tempDNA.slice(0, 8) };
    setLivinGenome(updatedGenome);
    setEditingDNA(false);
  };
  
  const cancelDNAEdits = () => {
    setTempDNA([]);
    setEditingDNA(false);
    setNewKeyword('');
  };
  
  const toggleDNAKeyword = (index) => {
    setTempDNA(prev => prev.filter((_, i) => i !== index));
  };
  
  const addDNAKeyword = () => {
    if (newKeyword.trim() && tempDNA.length < 8) {
      setTempDNA(prev => [...prev, newKeyword.trim()]);
      setNewKeyword('');
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);
  
  // Poll for status
  useEffect(() => {
    if (taskId) {
      pollInterval.current = setInterval(async () => {
        try {
          const res = await fetch(`/api/status/${taskId}`);
          const data = await res.json();
          setStatus(data);
          
          if (data.status === 'completed') {
            clearInterval(pollInterval.current);
            setIsGenerating(false);
            setTaskId(null);
            setHistory(prev => [...prev, data]);
            if (data.updated_state) {
              setLivinGenome(data.updated_state);
            }
            // Clear uploaded images after successful generation
            setReferenceImages([]);
            setEnvironmentImage(null);
            setSketchImage(null);
          } else if (data.status === 'failed') {
            clearInterval(pollInterval.current);
            setIsGenerating(false);
            setTaskId(null);
            alert("Generation failed: " + data.error);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 3000);
    }
    return () => clearInterval(pollInterval.current);
  }, [taskId]);
  
  // Persistence
  useEffect(() => {
    localStorage.setItem('dream_livin_history', JSON.stringify(history));
    localStorage.setItem('dream_livin_genome', JSON.stringify(livinGenome));
    localStorage.setItem('dream_livin_status', JSON.stringify(status));
  }, [history, livinGenome, status]);
  
  const handleGenerate = async () => {
    if (!feedback.trim() && livinGenome.round > 0 && referenceImages.length === 0 && !environmentImage && !sketchImage) {
      return;
    }
    
    setIsGenerating(true);
    setStatus({ status: 'queued' });
    
    try {
      const formData = new FormData();
      formData.append('feedback', feedback || "Start the initial exploration with diverse modular home concepts for Earth and Mars.");
      formData.append('state', JSON.stringify(livinGenome));
      
      // Append images
      referenceImages.forEach(img => {
        formData.append('reference_images', img.file);
      });
      
      if (environmentImage) {
        formData.append('environment_image', environmentImage.file);
      }
      
      if (sketchImage) {
        formData.append('sketch_image', sketchImage.file);
      }
      
      const res = await fetch('/api/feedback', {
        method: 'POST',
        body: formData
      });
      
      const data = await res.json();
      setTaskId(data.task_id);
      setFeedback('');
    } catch (err) {
      console.error("Generation error:", err);
      setIsGenerating(false);
    }
  };
  
  const currentDisplayData = currentView === 'current' ? status : history[currentView];
  const currentGenome = (currentView === 'current' || !history[currentView]?.updated_state)
    ? livinGenome
    : history[currentView].updated_state;
  
  const hasUploadedImages = referenceImages.length > 0 || environmentImage || sketchImage;
  
  return (
    <div className="app-container">
      <header>
        <div className="logo">
          <span className="logo-dream">DREAM</span>
          <span className="logo-livin">LIVIN</span>
          <span className="logo-shop">SHOP</span>
        </div>
        <div className="header-actions">
          <button
            className="btn-new-session"
            onClick={() => {
              if (window.confirm("Start a new session? This will clear all history and genome data.")) {
                setHistory([]);
                setStatus(null);
                setLivinGenome({
                  round: 0,
                  design_summary: '',
                  livin_dna: [],
                  confirmed_preferences: [],
                  rejected_elements: [],
                  feedback_history: []
                });
                setCurrentView('current');
                setReferenceImages([]);
                setEnvironmentImage(null);
                setSketchImage(null);
                localStorage.removeItem('dream_livin_history');
                localStorage.removeItem('dream_livin_genome');
                localStorage.removeItem('dream_livin_status');
              }
            }}
          >
            <RotateCcw size={14} />
            New Session
          </button>
        </div>
      </header>
      
      <div className="main-content">
        {/* Earth Group */}
        <div className="planet-group earth-group">
          <div className="planet-header">
            <Globe size={20} />
            <span>Earth Visions</span>
            <span className="strategy-tag">2 Evolve + 1 Explore</span>
          </div>
          
          {(!currentDisplayData || !currentDisplayData.earth_images?.length) && !isGenerating ? (
            <div className="empty-state">
              <Globe size={40} />
              <p>Earth concepts will appear here</p>
            </div>
          ) : (
            <div className="image-grid">
              {currentDisplayData?.earth_images?.map((img, i) => (
                <div key={i} className={`image-card ${img.type}`}>
                  <div className="type-badge">{img.type}</div>
                  <img src={img.url} alt={img.name} />
                  <div className="image-info">
                    <h4>{img.name}</h4>
                    <p>{img.prompt}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Mars Group */}
        <div className="planet-group mars-group">
          <div className="planet-header">
            <Rocket size={20} />
            <span>Mars Visions</span>
            <span className="strategy-tag">1 Evolve + 2 Explore</span>
          </div>
          
          {(!currentDisplayData || !currentDisplayData.mars_images?.length) && !isGenerating ? (
            <div className="empty-state">
              <Rocket size={40} />
              <p>Mars concepts will appear here</p>
            </div>
          ) : (
            <div className="image-grid">
              {currentDisplayData?.mars_images?.map((img, i) => (
                <div key={i} className={`image-card ${img.type}`}>
                  <div className="type-badge">{img.type}</div>
                  <img src={img.url} alt={img.name} />
                  <div className="image-info">
                    <h4>{img.name}</h4>
                    <p>{img.prompt}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="sidebar">
          {/* DNA Panel */}
          <div className="sidebar-section dna-panel">
            <div className="section-header">
              <Dna size={16} />
              <span>LIVIN DNA</span>
              {!editingDNA ? (
                <button className="btn-edit" onClick={startEditingDNA}>
                  <Edit3 size={14} />
                </button>
              ) : (
                <div className="edit-actions">
                  <button className="btn-save" onClick={saveDNAEdits}><Check size={14} /></button>
                  <button className="btn-cancel" onClick={cancelDNAEdits}><X size={14} /></button>
                </div>
              )}
            </div>
            
            {currentGenome.design_summary && (
              <div className="dna-summary">
                <ReactMarkdown>{currentGenome.design_summary}</ReactMarkdown>
              </div>
            )}
            
            <div className="dna-keywords">
              {editingDNA ? (
                <>
                  {tempDNA.map((keyword, i) => (
                    <span key={i} className="dna-tag editable" onClick={() => toggleDNAKeyword(i)}>
                      {keyword}
                      <X size={12} />
                    </span>
                  ))}
                  {tempDNA.length < 8 && (
                    <div className="add-keyword">
                      <input
                        type="text"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        placeholder="Add keyword..."
                        onKeyDown={(e) => e.key === 'Enter' && addDNAKeyword()}
                      />
                      <button onClick={addDNAKeyword}><Plus size={14} /></button>
                    </div>
                  )}
                </>
              ) : (
                currentGenome.livin_dna?.length > 0 ? (
                  currentGenome.livin_dna.map((keyword, i) => (
                    <span key={i} className="dna-tag">{keyword}</span>
                  ))
                ) : (
                  <span className="no-data">No DNA yet - start your journey!</span>
                )
              )}
            </div>
          </div>
          
          {/* History Panel */}
          <div className="sidebar-section history-panel">
            <div className="section-header">
              <History size={16} />
              <span>Journey History</span>
            </div>
            <div className="history-list">
              <div
                className={`history-item ${currentView === 'current' ? 'active' : ''}`}
                onClick={() => setCurrentView('current')}
              >
                Current Round {status?.round || livinGenome.round}
              </div>
              {[...history].reverse().filter(h => h.round !== (status?.round || livinGenome.round)).map((h) => {
                const originalIndex = history.indexOf(h);
                return (
                  <div
                    key={originalIndex}
                    className={`history-item ${currentView === originalIndex ? 'active' : ''}`}
                    onClick={() => setCurrentView(originalIndex)}
                  >
                    Round {h.round} Archive
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      
      {/* Input Controls */}
      <div className="controls">
        {/* Upload Section */}
        <div className="upload-section">
          <div className="upload-group">
            <label className="upload-btn" title="Reference Images (max 5)">
              <Image size={18} />
              <input type="file" accept="image/*" multiple onChange={handleReferenceUpload} />
              <span>Reference</span>
            </label>
            <label className="upload-btn" title="Environment Photo">
              <Globe size={18} />
              <input type="file" accept="image/*" onChange={handleEnvironmentUpload} />
              <span>Environment</span>
            </label>
            <label className="upload-btn" title="Sketch/Layout">
              <PenTool size={18} />
              <input type="file" accept="image/*" onChange={handleSketchUpload} />
              <span>Sketch</span>
            </label>
          </div>
          
          {hasUploadedImages && (
            <div className="uploaded-previews">
              {referenceImages.map((img, i) => (
                <div key={i} className="preview-thumb">
                  <img src={img.preview} alt={img.name} />
                  <button onClick={() => removeReferenceImage(i)}><X size={12} /></button>
                </div>
              ))}
              {environmentImage && (
                <div className="preview-thumb env">
                  <img src={environmentImage.preview} alt="Environment" />
                  <button onClick={() => setEnvironmentImage(null)}><X size={12} /></button>
                </div>
              )}
              {sketchImage && (
                <div className="preview-thumb sketch">
                  <img src={sketchImage.preview} alt="Sketch" />
                  <button onClick={() => setSketchImage(null)}><X size={12} /></button>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Text Input */}
        <div className="input-wrapper">
          {isRecording && (
            <div className="waveform-container">
              <div className="waveform">
                {audioLevels.map((level, i) => (
                  <div
                    key={i}
                    className="waveform-bar"
                    style={{
                      height: `${Math.max(level * 100, 5)}%`,
                      backgroundColor: `rgba(255, 107, 53, ${0.3 + level * 0.7})`
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          <textarea
            placeholder={livinGenome.round === 0 
              ? "Describe your dream modular home... What spaces do you envision? What feelings should it evoke?" 
              : "Share your thoughts on these visions... What resonates? What would you change?"}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={isGenerating || isRecording}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleGenerate();
              }
            }}
          />
          <div className="input-actions">
            {isTranscribing && (
              <div className="transcribing-indicator">
                <div className="loader small"></div>
                <span>Transcribing...</span>
              </div>
            )}
            <button
              className={`btn-voice ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isGenerating || isTranscribing}
            >
              {isRecording ? <Square size={20} /> : <Mic size={20} />}
            </button>
          </div>
        </div>
        
        {/* Generate Button */}
        <button
          className="btn-generate"
          onClick={handleGenerate}
          disabled={isGenerating || isRecording}
        >
          {isGenerating ? <div className="loader"></div> : <Sparkles size={28} />}
        </button>
      </div>
      
      {/* Status Overlay */}
      {isGenerating && (
        <div className="status-overlay">
          <div className="loader large"></div>
          <div className="status-text">
            <span className="status-main">{status?.status || 'Initializing...'}</span>
            <span className="status-sub">Creating your Earth & Mars visions...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
