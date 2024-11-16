// Copyright (C) 2012-present, The Authors. This program is free software: you can redistribute it and/or  modify it under the terms of the GNU Affero General Public License, version 3, as published by the Free Software Foundation. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import React from "react";
import _ from "lodash";
import * as globals from "./globals";

const computeVoteTotal = (users) => {
  let voteTotal = 0;

  _.each(users, (count) => {
    voteTotal += count;
  });

  return voteTotal;
};

// const computeUniqueCommenters = (comments) => {

// }

const Number = ({ number, label }) => (
  <div style={{ marginLeft: "10px", marginRight: "10px" }}>
    <p style={globals.overviewNumber}>{number.toLocaleString()}</p>
    <p style={globals.overviewLabel}>{label}</p>
  </div>
);

const pathname = window.location.pathname; // "/report/2arcefpshi"
const report_id = pathname.split("/")[2];
const doShowDataLicenseTerms = ["pol.is", "preprod.pol.is", "localhost"].includes(
  window.location.hostname
);

const getCurrentTimestamp = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}-${hours}${minutes}`;
};

const getDownloadFilename = (file, conversation) => {
  return `${getCurrentTimestamp()}-${conversation.conversation_id}-${file}.csv`;
};

const Overview = ({
  conversation,
  // demographics,
  ptptCount,
  ptptCountTotal,
  math,
  // comments,
  //stats,
  computedStats,
}) => {
  return (
    <div>
      <div>
        <p style={globals.primaryHeading}>Overview</p>
        <p style={globals.paragraph}>
          InnoPolis is a real-time survey system that helps identify the different ways a large
          group of people think about a divisive or complicated topic. InnoPolis is based on 
          <a href="https://pol.is/"> Polis</a> open-source codebase and adapted for the usage in
          web3-environment. Here’s a basic breakdown of some terms you’ll need to know in order
          to understand this report.
        </p>
        <p style={globals.paragraph}>
          <strong>Participants:</strong> These are the accounts who participated in the conversation
          by voting and writing statements. Based on how they voted, each participant is sorted into
          an opinion group.
        </p>
        <p style={globals.paragraph}>
          <strong>Statements:</strong> Participants may submit statements for other participants to
          vote on. Statements are assigned a number in the order they're submitted.
        </p>
        <p style={globals.paragraph}>
          <strong>Opinion groups:</strong> Groups are made of participants who voted similarly to
          each other, and differently from the other groups.
        </p>

        <p style={globals.paragraph}>
          {conversation && conversation.ownername
            ? "This InnoPolis conversation was run by " + conversation.ownername + ". "
            : null}
          {conversation && conversation.topic
            ? "The topic was '" + conversation.topic + "'. "
            : null}
        </p>
      </div>

      <div style={{ maxWidth: 1200, display: "flex", justifyContent: "space-between" }}>
        <Number number={ptptCountTotal} label={"accounts participated"} />
        <Number number={ptptCount} label={"accounts grouped"} />

        <Number number={computeVoteTotal(math["user-vote-counts"])} label={"votes were cast"} />
        {/* Leaving this out for now until we get smarter conversationStats */}
        {/* <Number number={comments.length} label={"people submitted statements"} /> */}
        <Number number={math["n-cmts"]} label={"statements were submitted"} />
        <Number
          number={computedStats.votesPerVoterAvg.toFixed(2)}
          label={"votes per voter on average"}
        />
        <Number
          number={computedStats.commentsPerCommenterAvg.toFixed(2)}
          label={"statements per author on average"}
        />
      </div>
    </div>
  );
};

export default Overview;

// <p style={globals.paragraph}> {conversation && conversation.participant_count ? "A total of "+ptptCount+" people participated. " : null} </p>

// It was presented {conversation ? conversation.medium : "loading"} to an audience of {conversation ? conversation.audiences : "loading"}.
// The conversation was run for {conversation ? conversation.duration : "loading"}.
// {demographics ? demographics.foo : "loading"} were women

// {conversation && conversation.description ? "The specific question was '"+conversation.description+"'. ": null}
