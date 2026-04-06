# Oil & Gas Production Repo

A Python-based project for analyzing and managing oil and gas production data.

## Project Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pcarun606-cyber/Oil-gas-production-repo.git
cd Oil-gas-production-repo
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   - **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure
```
Oil-gas-production-repo/
├── src/                    # Source code
├── tests/                  # Unit tests
├── data/                   # Data files
├── notebooks/              # Jupyter notebooks
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Development

To run the application:
```bash
python -m src.main
```

To run tests:
```bash
pytest tests/
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

MIT License
