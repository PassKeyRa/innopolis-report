// Copyright (C) 2012-present, The Authors. This program is free software: you can redistribute it and/or  modify it under the terms of the GNU Affero General Public License, version 3, as published by the Free Software Foundation. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

import React from "react";
import SmallLogo from "./logoSmallLong";
import Url from "../../util/url";

//const urlPrefix = Url.urlPrefix;

function getUrlParameter(name) {
  const searchParams = new URLSearchParams(window.location.search);
  return searchParams.get(name);
}

const chain = getUrlParameter('chain');
const report_id = getUrlParameter('report_id');
const blockscoutUrl = "blockscout.com";
const urlPrefix = chain ? `https://${chain}.${blockscoutUrl}/` : `https://${blockscoutUrl}/`;

const Content = ({conversation}) => {
  return (
    <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-end",
        width: "100%",
        paddingBottom: 5,
        borderBottom: "1px solid rgb(130,130,130)",
      }}>
      <SmallLogo/>
      <p style={{
          fontSize: 36,
          margin: 0,
        }}>
        Report
      </p>
      <p style={{
          fontSize: 24,
          margin: 0,
        }}>
        <a
          style={{color: "#48ae20", fontWeight: 700, textDecoration: "none"}}
          href={`${urlPrefix + report_id}`}>{urlPrefix + report_id}
        </a>
      </p>
    </div>
  );
}

const Heading = ({conversation}) => {
 return (
   <div>
     {conversation ? <Content conversation={conversation}/> : "Loading..."}
   </div>
 )
};

export default Heading;
