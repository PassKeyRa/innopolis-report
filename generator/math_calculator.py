import subprocess
import os
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

def calculate(database_url: str, zid: str, working_dir: str = "./math", timeout: int = 60) -> str:
    work_path = Path(working_dir)
    if not work_path.exists():
        raise FileNotFoundError(f"Working directory {working_dir} does not exist")

    env = os.environ.copy()
    env['DATABASE_URL'] = database_url

    logger.info(f"Starting calculation for ZID: {zid}")
    logger.info(f"Working directory: {working_dir}")

    try:
        process = subprocess.Popen(
            ['clojure', '-M:run', 'update', '-z', str(zid)],
            cwd=working_dir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        
        output = []
        start_time = time.time()
        # Read output in real-time
        while True:
            if time.time() - start_time > timeout:
                process.kill()
                error_msg = f"Process timed out after {timeout} seconds"
                logger.error(error_msg)
                raise TimeoutError(error_msg)

            line = process.stdout.readline()
            error_line = process.stderr.readline()
            if not line and not error_line and process.poll() is not None:
                break
            if line:
                print(line.rstrip())
                output.append(line)
            if error_line:
                print(error_line.rstrip())
                output.append(error_line)
                
        # Get the return code and any errors
        return_code = process.wait()
        stderr = process.stderr.read()
        
        if return_code != 0:
            error_msg = f"Clojure command failed with exit code {return_code}\nError: {stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        if stderr:
            logger.warning(f"Command stderr:\n{stderr}")
            
        logger.info(f"Math update for conversation id {zid} completed successfully")
        logger.debug(f"Command output:\n{output}")
        
        return output

    except subprocess.CalledProcessError as e:
        error_msg = f"Clojure command failed with exit code {e.returncode}\nOutput: {e.stdout}\nError: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except FileNotFoundError:
        error_msg = "Clojure command not found. Make sure Clojure is installed and in PATH"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

