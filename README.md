# Innopolis Report

A comprehensive reporting system with generator and client components for blockchain-based discussions.

## Project Structure

The repository consists of three main components:

- `generator/` - Python-based report generation service
- `client-report/` - React-based report viewing interface
- `InnoPolis-frontend/` - Frontend submodule (separate repository)

## Generator Service

### Prerequisites

- Python 3.x
- PostgreSQL client
- Virtual environment (recommended)

### Dependencies
```python
eth_abi==5.1.0
Flask==3.1.0
psycopg2-binary==2.9.10
python-dotenv==1.0.1
web3==7.5.0
```

### Installation
```bash
cd generator
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Client Report

### Prerequisites

- Node.js
- NPM

### Installation
```bash
cd client-report
npm install
```


### Available Scripts

- `npm start` - Runs the webpack dev server for development
- `npm run build:prod` - Builds static assets for production deployment

### Environment Variables

- `SERVICE_URL` - (Optional) API Server URL
- AWS credentials at `.polis_s3_creds_client.json` for S3 bucket deployment

## Development Setup

1. Clone the repository with submodules:
   ```bash
   git clone --recursive https://github.com/[username]/innopolis-report.git
   ```

2. If you've already cloned the repository:
   ```bash
   git submodule update --init --recursive
   ```

3. Set up each component following their respective installation instructions

## Docker Support

The project includes Docker configurations for development and deployment:

- `.dockerignore` files are configured for each component
- Generator service includes Python-specific Docker configurations
- Client report includes Node.js-based Docker setup

## File Structure
```
innopolis-report/
├── generator/
│ ├── math/
│ ├── requirements.txt
│ └── test-data/
├── client-report/
│ ├── public/
│ ├── src/
│ └── package.json
└── InnoPolis-frontend/ (submodule)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GNU Affero General Public License - see the LICENSE files in respective components for details.

## Ignored Files

The following files and directories are ignored in version control:
```
.env
venvpycache
.swp
node_modules
output
```

Make sure to properly configure these files in your development environment.
