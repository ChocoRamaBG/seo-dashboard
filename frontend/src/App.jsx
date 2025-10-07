import { useState, useRef, useEffect } from "react";
import './App.css';

function App() {
  const [domain, setDomain] = useState("buzzmaker.digital");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(-1);

  const controllerRef = useRef(null);

  const steps = [
      "Initializing analysis…",
      "Fetching SEO Data…",
      "Parsing HTML structure…",
      "Analyzing Keywords…",
      "Checking Backlinks…",
      "Optimizing Content…",
      "Running Final Checks…",
      "Finalizing report…",
      "Almost Ready…"
    ];



  // въртим стъпките, докато е активен loading
  useEffect(() => {
    if (!loading) return;
    const timeout = setTimeout(() => setLoadingStep(0), 100); // забавяне 100ms
    const interval = setInterval(() => {
      setLoadingStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          return prev; // задържа последната
        }
      });
    }, 2700); //2700 perfect balance
    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [loading]);


  const analyzeSite = async () => {
    setLoading(true);
    controllerRef.current = new AbortController();

    try {
      const response = await fetch(
        `https://seo-dashboard-hj2d.onrender.com/api/analyze?domain=${domain}`,
        { signal: controllerRef.current.signal }
      );
      const result = await response.json();
      setData(result);
    } catch (err) {
      if (err.name === "AbortError") {
        console.log("Заявката е прекъсната от потребителя");
      } else {
        console.error(err);
        alert("Error fetching data from backend");
      }
    }
    setLoading(false);
  };

  const cancelLoading = () => {
    if (controllerRef.current) {
      controllerRef.current.abort();
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="custom-header">
        <div className="header-container">
          <div className="logo-section">
            <div className="logo-icon">📊</div>
            <div className="logo-text">
              <p className="logo-title">SEO Analytics</p>
              <p className="logo-subtitle">Professional website insights</p>
            </div>
          </div>
          <nav className="menu">
            <button className="menu-btn">Analyze</button>
            <button className="menu-btn">Optimize</button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <h1 className="hero-title">SEO Analytics Dashboard</h1>
          <p className="hero-subtitle">
            Get comprehensive insights into your website's SEO performance, traffic patterns, and keyword rankings in a business-friendly format.
          </p>

          <div className="hero-card">
            <h2 className="hero-card-title">🌐 Website Analysis</h2>
            <p className="hero-card-subtitle">
              Enter your website URL to get comprehensive SEO insights including traffic data, keyword rankings, and backlink analysis
            </p>

            {/* Form */}
            <form
              className="hero-inputs"
              onSubmit={(e) => {
                e.preventDefault();
                analyzeSite();
              }}
            >
              <input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="Enter website URL (e.g., example.com)"
                className="hero-input"
              />
              <button type="submit" className="hero-btn">
                Analyze
              </button>
            </form>

            <div className="hero-examples">
              {["buzzmaker.digital", "vig.re", "facebook.com"].map((ex) => (
                <button
                  key={ex}
                  onClick={() => setDomain(ex)}
                  className="hero-example-btn"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Loading Modal */}
      {loading && (
        <div className="modal-overlay">
          <div className="modal">
            <button className="close-btn" onClick={cancelLoading}>✖</button>
            <div className="spinner"></div>
            <p>{steps[loadingStep]}</p>



            <div className="progress-bar">
              <div
                className="progress"
                style={{
                  width:
                    loadingStep < 0
                      ? '0%'
                      : `${((loadingStep + 1) / steps.length) * 100}%`,
                  transition: 'width 0.5s ease-in-out'
                }}
              />
            </div>



          </div>
        </div>
      )}

      {/* JSON Output */}
      {data && (
        <main className="cards-grid">
          <div className="card text-left">
            <h3 className="font-semibold text-gray-700 mb-3">Raw JSON Output</h3>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
