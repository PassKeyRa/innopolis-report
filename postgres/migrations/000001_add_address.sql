ALTER TABLE conversations 
ADD COLUMN address VARCHAR(42);
CREATE INDEX conversations_address_idx ON conversations(address); 