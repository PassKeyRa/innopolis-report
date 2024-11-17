# InnoPolis

A decentralized platform for community engagement and decision-making with ML-powered opinion analysis.

# What is InnoPolis
InnoPolis is a decentralized version of [pol.is](https://pol.is/home). Polis is an open-source technology for surveys (or wikisurveys, to be more precise). It is a system that allows people to submit statements about an issue, and vote on each other's statements (agree/disagree/pass). Machine learning is used to process the data and transform it into a report, where major clusters in the different points of view could be seen and analyzed. It helps with finding major points of consensus, disagreement or misunderstanding between participants.

# Why InnoPolis?

While Polis is a powerful deliberation tool, it has yet to be widely adopted by cryptocurrency communities. InnoPolis bridges this gap by providing:

## Community Definition
Flexible community identification through various on-chain credentials:
  - ERC20 holdings
  - NFT holdings
  - ENS
  - Custom Authentication 

## Data-Driven Insights
- Standardized reporting of collective sentiment and ideas
- Statistical analysis of community consensus and divergence
- Visual representation of opinion clusters

## Use Cases
- Enhanced DAO governance and decision-making processes
- Direct feedback channels between developers and users
- Collective expression tools for Web3 communities
- Community sentiment analysis and trend identification

## Data

All data is stored on chain, therefore it can not be deleted or modified. There is frontend page to generate report. This frontend takes data from blockchain and generates HTML page with vote statistics. Anyone can launch docker image to generate report locally.

## Project Structure

The repository consists of several components:

- `innopolis-contracts/` - Solidity contracts responsible for storing conversations data and managing the voting process
- `InnoPolis-frontend/` - Frontend part for interacting with the platform
- `generator/` - Python-based report generation service. Uses the modified math module from Polis 
- `client-report/` - React-based report viewing interface (based on original Polis `client-report` service)

## Contracts

Each survey (conversation) is represented by the `Conversation.sol` contract. It stores all the data about the conversation and manages the voting process. To create a new conversation, one needs to deploy the instance of this contract using the `ConversationFactory.sol` contract.

In addition, a conversation can have authentication manager, which is responsible for checking if the user is authenticated to participate in the conversation. Currently, there are three template authentication managers implemented:
- `ENSHoldingManager.sol` - Checks if the user has an ENS name
- `ERC20HoldingManager.sol` - Checks if the user has a certain ERC20 token
- `NFTHoldingManager.sol` - Checks if the user has a certain NFT

However, one can implement their own authentication manager with any custom authentication logic.

## Generator Service

The generator service is a Python-based application that processes data from conversations on chain and generates a report. It can be run either as a CLI application or as a HTTP server.

### Run as CLI application

To run the generator as a CLI application, one needs to set up the environment and install the dependencies:

```bash
cd generator
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip3 install -r requirements.txt
```

The generator uses PostgreSQL database to store the conversations data. The `docker-compose.local.yml` file contains the configuration for the local development environment with PostgreSQL. Copy the `.env.example` file to `.env` and modify the environment variables according to your PostgreSQL database configuration.

After that, run the generator with the following command:
```bash
python3 main.py cli --chain <chain name> --address <conversation contract address> --output <output json file>
```

### Run as an HTTP server

The full configuration including database, generator as an HTTP server, frontend and report viewer services can be run using `docker-compose.yml` file.

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
